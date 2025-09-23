const BASE_URL = "http://127.0.0.1:8000";

export async function listVideos() {
    const res = await fetch(`${BASE_URL}/list-videos`);
    return await res.json();
}

export async function analyzeVideo(videoPath) {
    const res = await fetch(`${BASE_URL}/analyze-video`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ video_path: videoPath })
    });
    return await res.json();
}
