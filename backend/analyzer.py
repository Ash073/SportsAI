from models.ai.motion_analysis import analyze_pushups, integrate_your_model
import os
import logging
from typing import List, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_videos(base_path="data") -> Tuple[List[str], List[str]]:
    """Load training videos from correct and wrong directories."""
    try:
        correct_dir = os.path.join(base_path, "correct")
        wrong_dir = os.path.join(base_path, "wrong")
        
        correct_videos = []
        wrong_videos = []
        
        if os.path.exists(correct_dir):
            correct_videos = [os.path.join(correct_dir, f)
                            for f in os.listdir(correct_dir)
                            if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv"))]
        
        if os.path.exists(wrong_dir):
            wrong_videos = [os.path.join(wrong_dir, f)
                          for f in os.listdir(wrong_dir)
                          if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv"))]
        
        logger.info(f"Loaded {len(correct_videos)} correct videos and {len(wrong_videos)} wrong videos")
        return correct_videos, wrong_videos
        
    except Exception as e:
        logger.error(f"Error loading videos: {str(e)}")
        return [], []

def process_video(video_path: str, exercise: str = "pushups") -> str:
    """Process video and return analysis results."""
    try:
        logger.info(f"Processing video: {video_path} for exercise: {exercise}")
        
        # Validate video file
        if not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return '{"error": "Video file not found"}'
        
        # Check file size (basic validation)
        file_size = os.path.getsize(video_path)
        if file_size == 0:
            logger.error(f"Video file is empty: {video_path}")
            return '{"error": "Video file is empty"}'
        
        # Route to appropriate analysis function based on exercise type
        if exercise.lower() in ["pushup", "pushups", "push-up", "push-ups"]:
            result = analyze_pushups(video_path)
        else:
            # For other exercises, you can add more analysis functions
            logger.warning(f"Exercise type '{exercise}' not specifically supported, using pushup analysis")
            result = analyze_pushups(video_path)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing video {video_path}: {str(e)}")
        return f'{{"error": "Failed to process video: {str(e)}"}}'
