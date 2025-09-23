// src/components/Dashboard.tsx
import React, { useEffect, useState } from "react";
import { listVideos, analyzeVideo, uploadVideo } from "./api.tsx";
import type { VideoAnalysisResult } from "./api.tsx";

const Dashboard: React.FC = () => {
  const [videos, setVideos] = useState<string[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<VideoAnalysisResult | null>(null);
  const [uploading, setUploading] = useState(false);

  // Fetch video list when component loads
  useEffect(() => {
    (async () => {
      try {
        const data = await listVideos();
        setVideos(data.videos);
      } catch (error) {
        console.error("Error fetching videos:", error);
      }
    })();
  }, []);

  // Handle video upload
  const handleUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setUploading(true);
      try {
        await uploadVideo(event.target.files[0]);
        const data = await listVideos();
        setVideos(data.videos);
      } catch (error) {
        console.error("Upload failed:", error);
      } finally {
        setUploading(false);
      }
    }
  };

  // Handle analysis
  const handleAnalyze = async (video: string) => {
    setSelectedVideo(video);
    try {
      const result = await analyzeVideo(video);
      setAnalysis(result);
    } catch (error) {
      console.error("Analysis failed:", error);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>🏋️ Sports AI Dashboard</h1>

      {/* Upload Section */}
      <input type="file" accept="video/*" onChange={handleUpload} />
      {uploading && <p>Uploading...</p>}

      {/* Video List */}
      <h2>Available Videos</h2>
      <ul>
        {videos.map((video) => (
          <li key={video}>
            {video}{" "}
            <button onClick={() => handleAnalyze(video)}>Analyze</button>
          </li>
        ))}
      </ul>

      {/* Analysis Results */}
      {analysis && selectedVideo && (
        <div style={{ marginTop: "20px" }}>
          <h2>📊 Analysis Results for {selectedVideo}</h2>
          <p>✅ Pushups: {analysis.pushups}</p>
          <p>⏱️ Duration: {analysis.duration_sec.toFixed(2)} sec</p>
          <p>⚡ Avg Speed: {analysis.avg_speed.toFixed(2)}</p>
          <p>📏 Distance Moved: {analysis.distance_moved.toFixed(2)}</p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
