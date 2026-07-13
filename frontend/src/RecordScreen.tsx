import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { UploadIcon, VideoIcon, CheckCircleIcon } from './icons';

interface RecordScreenProps {
  onNavigate: (route: string, data?: any) => void;
  userId?: number;
  isAuthenticated?: boolean;
}

export default function RecordScreen({ onNavigate, userId, isAuthenticated }: RecordScreenProps) {
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const recordedChunksRef = useRef<Blob[]>([]);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('video/')) {
      setSelectedFile(file);
    } else {
      alert('Please select a video file');
    }
  };

  const uploadVideo = async () => {
    if (!selectedFile) {
      alert('Please select a video file first');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('exercise', 'pushup');
    if (userId) {
      formData.append('user_id', userId.toString());
    }

    try {
      const token = localStorage.getItem('ae_token');
      const response = await axios.post('https://sports-ai-a2xm.onrender.com/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
      });
      onNavigate('result', { result: response.data });
    } catch (error: any) {
      console.error('Upload error:', error);
      const status = error?.response?.status;
      const detail = error?.response?.data?.detail || error?.message || 'Unknown error';
      alert(`Upload failed${status ? ` (HTTP ${status})` : ''}: ${detail}`);
    } finally {
      setUploading(false);
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 }, audio: true });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setIsCameraOn(true);
      setRecordedBlob(null);
    } catch (e) {
      console.error('Camera error:', e);
      alert('Unable to access camera/microphone. Please check permissions.');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCameraOn(false);
  };

  const startRecording = () => {
    if (!streamRef.current) {
      alert('Camera is not started. Start the camera first.');
      return;
    }
    recordedChunksRef.current = [];
    const mimeType = 'video/webm;codecs=vp9,opus';
    const options = MediaRecorder.isTypeSupported(mimeType) ? { mimeType } : undefined as any;
    const recorder = new MediaRecorder(streamRef.current, options);
    mediaRecorderRef.current = recorder;
    recorder.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) {
        recordedChunksRef.current.push(e.data);
      }
    };
    recorder.onstop = () => {
      const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
      setRecordedBlob(blob);
      const file = new File([blob], `recording_${Date.now()}.webm`, { type: 'video/webm' });
      setSelectedFile(file);
    };
    recorder.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== 'inactive') {
      recorder.stop();
    }
    setIsRecording(false);
  };

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(t => t.stop());
      }
    };
  }, []);

  return (
    <div className="container">
      <div className="card">
        <div className="header">
          <h1 className="title">Athlete's Edge AI</h1>
          <p className="subtitle">Advanced motion analysis for athletic performance</p>
        </div>
        
        <div className="upload-section">
          <h2 className="section-title">
            <UploadIcon size={20} />
            Upload Video
          </h2>
          
          <div className="file-input-container">
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              onChange={handleFileSelect}
              className="file-input"
            />
            <label className="file-input-label">
              <VideoIcon size={24} />
              {selectedFile ? 'Change video file' : 'Choose video file'}
            </label>
          </div>
          
          {selectedFile && (
            <div className="file-selected">
              <CheckCircleIcon size={16} />
              <span>{selectedFile.name}</span>
            </div>
          )}
          
          <button 
            className="btn" 
            onClick={uploadVideo} 
            disabled={!selectedFile || uploading}
          >
            {uploading ? (
              <>
                <div className="loading-spinner" />
                Analyzing...
              </>
            ) : (
              <>
                <UploadIcon size={16} />
                Upload & Analyze
              </>
            )}
          </button>
        </div>

        <div className="divider"></div>

        <div className="record-section">
          <h2 className="section-title">
            <VideoIcon size={20} />
            Record New Video
          </h2>
          <div className="camera-area">
            <div className="camera-preview">
              <video ref={videoRef} playsInline muted className="camera-video" />
            </div>
            <div className="camera-controls">
              {!isCameraOn ? (
                <button className="btn" onClick={startCamera}>
                  <VideoIcon size={16} /> Start Camera
                </button>
              ) : (
                <>
                  {!isRecording ? (
                    <button className="btn" onClick={startRecording}>
                      <VideoIcon size={16} /> Start Recording
                    </button>
                  ) : (
                    <button className="btn" onClick={stopRecording}>
                      <VideoIcon size={16} /> Stop Recording
                    </button>
                  )}
                  <button className="btn btn-secondary" onClick={stopCamera}>
                    Stop Camera
                  </button>
                </>
              )}
            </div>
            {recordedBlob && (
              <div className="file-selected" style={{ marginTop: '0.75rem' }}>
                <CheckCircleIcon size={16} />
                <span>Recording ready. You can upload now.</span>
              </div>
            )}
          </div>
          <button
            className="btn"
            onClick={uploadVideo}
            disabled={!selectedFile || uploading}
            style={{ marginTop: '0.75rem' }}
          >
            {uploading ? (
              <>
                <div className="loading-spinner" />
                Uploading...
              </>
            ) : (
              <>
                <UploadIcon size={16} />
                Upload Recorded Video
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}