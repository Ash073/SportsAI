async function listVideos() {
    const res = await fetch('http://127.0.0.1:8000/list-videos');
    const data = await res.json();
    document.getElementById('videos').textContent = JSON.stringify(data, null, 2);
}

async function analyzeVideo() {
    const videoPath = document.getElementById('videoPath').value;
    const res = await fetch('http://127.0.0.1:8000/analyze-video', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({video_path: videoPath})
    });
    const data = await res.json();
    document.getElementById('result').textContent = JSON.stringify(data, null, 2);
}
