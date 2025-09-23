// src/api.ts
const BASE_URL = "http://127.0.0.1:8000";

export interface VideoAnalysisResult {
  pushups: number;
  duration_sec: number;
  avg_speed: number;
  distance_moved: number;
}

export interface VideoListResponse {
  videos: string[];
}

export async function listVideos(): Promise<VideoListResponse> {
  const res = await fetch(`${BASE_URL}/list-videos`);
  if (!res.ok) throw new Error("Failed to fetch videos");
  return await res.json() as VideoListResponse;
}

export async function analyzeVideo(videoPath: string): Promise<VideoAnalysisResult> {
  const res = await fetch(`${BASE_URL}/analyze-video?video_path=${encodeURIComponent(videoPath)}`, {
    method: "POST"
  });
  if (!res.ok) throw new Error("Failed to analyze video");
  return await res.json() as VideoAnalysisResult;
}

export async function uploadVideo(file: File): Promise<{ message: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/upload-video`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Failed to upload video");
  return await res.json() as { message: string };
}
