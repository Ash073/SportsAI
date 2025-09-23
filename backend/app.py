from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

@app.get("/list-videos")
def list_videos():
    return {"videos": os.listdir(VIDEO_DIR)}

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    file_path = os.path.join(VIDEO_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"message": "Video uploaded successfully", "file": file.filename}

@app.post("/analyze-video")
def analyze_video(video_path: str):
    # dummy response for now
    return {
        "pushups": 12,
        "duration_sec": 45.6,
        "avg_speed": 1.2,
        "distance_moved": 0.9
    }
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import JSONResponse
from analyzer import process_video
import shutil, os, json

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...), 
    exercise: str = Form(...)
):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save uploaded video
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Run analysis
    result = process_video(file_path, exercise)

    # Save results
    with open("storage.json", "a") as f:
        f.write(result + "\n")

    return JSONResponse(content=json.loads(result))
