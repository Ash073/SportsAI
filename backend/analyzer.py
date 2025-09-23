from ai_model.motion_analysis import analyze_pushups
import os

def load_videos(base_path="data"):
    correct_videos = [os.path.join(base_path, "correct", f)
                      for f in os.listdir(os.path.join(base_path, "correct"))
                      if f.endswith((".mp4", ".avi", ".mov"))]

    wrong_videos = [os.path.join(base_path, "wrong", f)
                    for f in os.listdir(os.path.join(base_path, "wrong"))
                    if f.endswith((".mp4", ".avi", ".mov"))]

    return correct_videos, wrong_videos

def process_video(video_path: str):
    result = analyze_pushups(video_path)
    return result
