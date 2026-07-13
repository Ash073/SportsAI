from fastapi import FastAPI, UploadFile, Form, File, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from analyzer import process_video
import subprocess
import shutil, os, json
import uvicorn
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from database import get_db, create_tables, test_connection, User, Workout
from user_service import UserService, WorkoutService
from pydantic import BaseModel, Field
from typing import Optional, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username must be 3-50 characters")
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$', description="Valid email address required")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name (optional)")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "securepassword",
                "full_name": "John Doe"
            }
        }

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    
    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "securepassword"
            }
        }

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    total_workouts: int
    total_pushups: int
    best_form_score: float
    avg_form_score: float
    created_at: datetime

class WorkoutResponse(BaseModel):
    id: int
    exercise_type: str
    pushup_count: int
    duration_sec: float
    form_score: float
    avg_speed: Optional[float]
    total_distance: Optional[float]
    ai_confidence: Optional[float]
    model_used: Optional[str]
    video_filename: Optional[str]
    analysis_notes: Optional[str]
    created_at: datetime
    processing_status: str

# Initialize database
try:
    if test_connection():
        create_tables()
        logger.info("Database initialized successfully")
    else:
        logger.warning("Database connection failed, running without persistence")
except Exception as e:
    logger.error(f"Database initialization error: {e}")
    logger.warning("Running in file-based mode")

app = FastAPI(title="Athlete's Edge AI API", description="Motion analysis for athletic performance", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dataset directories for training data
DATA_DIR = "data"
DATA_CORRECT_DIR = os.path.join(DATA_DIR, "correct")
DATA_WRONG_DIR = os.path.join(DATA_DIR, "wrong")
os.makedirs(DATA_CORRECT_DIR, exist_ok=True)
os.makedirs(DATA_WRONG_DIR, exist_ok=True)

# Import dataset-trained analyzer utilities (used for retraining)
try:
    from dataset_trained_model import get_dataset_analyzer
except Exception as _e:
    get_dataset_analyzer = None

# Authentication helpers
def verify_token(authorization: str = Header(None)):
    """Simple token verification - replace with proper JWT in production"""
    if not authorization:
        return None
    
    try:
        # Extract token from "Bearer token" format
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            if token.startswith("token_"):
                user_id = int(token.replace("token_", ""))
                return user_id
    except (ValueError, AttributeError):
        pass
    
    return None

def get_current_user_optional(authorization: str = Header(None)):
    """Get current user if authenticated, otherwise return None"""
    return verify_token(authorization)

def get_current_user_required(authorization: str = Header(None)):
    """Require authentication and return user_id"""
    user_id = verify_token(authorization)
    if not user_id:
        raise HTTPException(
            status_code=401, 
            detail="Authentication required. Please login first.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id

@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "message": "Athlete's Edge AI API is running",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "/upload": "POST - Upload video for analysis",
            "/list-videos": "GET - List uploaded videos",
            "/analyze-video": "POST - Analyze specific video"
        }
    }

@app.get("/list-videos")
def list_videos():
    """List all uploaded videos."""
    try:
        videos = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv", ".webm"))]
        uploads = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith((".mp4", ".avi", ".mov", ".mkv", ".webm"))]
        
        return {
            "videos_dir": videos,
            "uploads_dir": uploads,
            "total_count": len(videos) + len(uploads)
        }
    except Exception as e:
        logger.error(f"Error listing videos: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list videos")

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    file_path = os.path.join(VIDEO_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"message": "Video uploaded successfully", "file": file.filename}

@app.post("/analyze-video")
async def analyze_video(request: dict):
    video_path = request.get("video_path")
    if not video_path:
        return {"error": "video_path is required"}
    
    # dummy response for now
    return {
        "pushups": 12,
        "duration_sec": 45.6,
        "avg_speed": 1.2,
        "distance_moved": 0.9
    }

def normalize_video(input_path: str) -> str:
    """
    Skip transcoding completely for performance.
    We assume the uploaded video is readable by OpenCV.
    """
    logger.info(f"Skipping ffmpeg normalization for {input_path}")
    return input_path

@app.post("/upload")
async def upload_for_analysis(
    file: UploadFile = File(..., description="Video file to analyze"),
    exercise: str = Form("pushups", description="Exercise type (pushups, squats, etc.)"),
    user_id: int = Form(1, description="User ID for tracking")
):
    """Upload video file and perform analysis."""
    try:
        # Input validation
        if not file or not file.filename:
            raise HTTPException(
                status_code=422, 
                detail="No file provided. Please select a video file to upload."
            )
        
        # Validate file type - improved validation
        allowed_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        file_extension = os.path.splitext(file.filename.lower())[1] if file.filename else ''
        
        if not file_extension or file_extension not in allowed_extensions:
            logger.warning(f"Invalid file extension: {file_extension} for file: {file.filename}")
            raise HTTPException(
                status_code=422, 
                detail=f"Invalid file type. Only video files ({', '.join(allowed_extensions)}) are allowed."
            )
        
        # Validate exercise type
        valid_exercises = ['pushups', 'pushup', 'push-ups', 'squats', 'squat']
        if exercise.lower() not in valid_exercises:
            logger.warning(f"Invalid exercise type: {exercise}")
            raise HTTPException(
                status_code=422,
                detail=f"Invalid exercise type '{exercise}'. Supported: {', '.join(valid_exercises)}"
            )
        
        # Read and validate file size
        try:
            file_content = await file.read()
        except Exception as e:
            logger.error(f"Error reading uploaded file: {e}")
            raise HTTPException(status_code=422, detail="Error reading uploaded file. File may be corrupted.")
        
        if len(file_content) == 0:
            raise HTTPException(status_code=422, detail="Uploaded file is empty.")
        
        # Validate file size (max 100MB)
        max_file_size = 100 * 1024 * 1024  # 100MB
        if len(file_content) > max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large ({len(file_content) / 1024 / 1024:.1f}MB). Maximum size is 100MB."
            )
        
        # Validate user_id
        if user_id <= 0:
            raise HTTPException(status_code=422, detail="Invalid user_id. Must be a positive integer.")
        
        # Reset file pointer and save file
        await file.seek(0)
        
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        logger.info(f"Saving uploaded file: {filename} ({len(file_content)} bytes)")
        
        # Save uploaded video
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        logger.info(f"Starting analysis for: {filename}")
        
        # Normalize to a consistent format for analysis
        normalized_path = normalize_video(file_path)
        # Run analysis
        result = process_video(normalized_path, exercise)
        
        # Parse and validate result
        try:
            result_dict = json.loads(result)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from analysis: {e}")
            raise HTTPException(status_code=500, detail="Analysis returned invalid data")
        
        # Add metadata
        result_dict["upload_timestamp"] = timestamp
        result_dict["original_filename"] = file.filename
        result_dict["file_size_bytes"] = len(file_content)
        
        # Save results with better formatting
        storage_entry = {
            "timestamp": timestamp,
            "filename": filename,
            "original_filename": file.filename,
            "exercise": exercise,
            "results": result_dict
        }
        
        with open("storage.json", "a") as f:
            f.write(json.dumps(storage_entry) + "\n")
        
        logger.info(f"Analysis completed successfully for: {filename}")
        
        # Save to database if available
        try:
            db = next(get_db())
            
            workout_service = WorkoutService(db)
            workout_service.save_workout(user_id, result_dict, filename)
            logger.info(f"Workout saved to database for user {user_id}")
            
        except Exception as db_error:
            logger.warning(f"Failed to save to database: {db_error}")
            # Continue without database - fallback to file storage
        
        return JSONResponse(content=result_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during upload/analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/analyze-for-ai-suggestions")
async def analyze_for_ai_suggestions(
    file: UploadFile = File(...),
    exercise: str = Form("pushups"),
    user_id: int = Form(1)  # Default to user 1 for testing
):
    """
    Analyze exercise video and return results formatted for AI improvement suggestions.
    Returns format: {exercise, count, form_score, issues}
    """
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size (max 100MB)
        max_file_size = 100 * 1024 * 1024  # 100MB
        file_content = await file.read()
        if len(file_content) > max_file_size:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 100MB")
        
        # Reset file pointer and save file
        await file.seek(0)
        
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        logger.info(f"Processing for AI suggestions: {filename} ({len(file_content)} bytes)")
        
        # Save uploaded video
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Run analysis specifically for AI suggestions
        try:
            from ai_exercise_analyzer import analyze_pushups_for_ai_suggestions  # type: ignore
            result = analyze_pushups_for_ai_suggestions(file_path)
            logger.info(f"AI suggestions analysis completed for: {filename}")
            
        except ImportError:
            logger.warning("AI analyzer not available, using fallback")
            # Fallback to mock format
            result = json.dumps({
                "exercise": "pushup",
                "count": 8,
                "form_score": 75,
                "issues": ["elbows too wide", "incomplete depth"]
            })
        
        # Parse result
        try:
            result_dict = json.loads(result)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from AI suggestions analysis: {e}")
            raise HTTPException(status_code=500, detail="Analysis returned invalid data")
        
        logger.info(f"AI suggestions result: {result_dict}")
        return JSONResponse(content=result_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during AI suggestions analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/get-improvement-suggestions")
async def get_improvement_suggestions(
    file: UploadFile = File(..., description="Video file to analyze"),
    exercise: str = Form("pushups", description="Exercise type"),
    user_id: int = Form(1, description="User ID")
):
    """
    Complete workflow: Analyze video and get AI improvement suggestions from Gemini.
    Returns both analysis and personalized suggestions.
    """
    
    try:
        # First, get the AI analysis in the format needed
        # Reuse the validation from analyze_for_ai_suggestions
        
        # Input validation
        if not file or not file.filename:
            raise HTTPException(
                status_code=422, 
                detail="No file provided. Please select a video file to upload."
            )
        
        # Validate file type
        allowed_types = ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime', 'video/x-msvideo', 'video/webm']
        if not file.content_type or file.content_type not in allowed_types:
            raise HTTPException(
                status_code=422, 
                detail=f"Invalid file type '{file.content_type}'. Only video files (MP4, AVI, MOV) are allowed."
            )
        
        # Read and validate file
        try:
            file_content = await file.read()
        except Exception as e:
            logger.error(f"Error reading uploaded file: {e}")
            raise HTTPException(status_code=422, detail="Error reading uploaded file. File may be corrupted.")
        
        if len(file_content) == 0:
            raise HTTPException(status_code=422, detail="Uploaded file is empty.")
        
        # Validate file size (max 100MB)
        max_file_size = 100 * 1024 * 1024  # 100MB
        if len(file_content) > max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large ({len(file_content) / 1024 / 1024:.1f}MB). Maximum size is 100MB."
            )
        
        # Save the uploaded file
        await file.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Normalize to consistent format before analysis
        normalized_path = normalize_video(file_path)
        # Get AI analysis in the format needed for Gemini
        try:
            from ai_exercise_analyzer import analyze_pushups_for_ai_suggestions  # type: ignore
            analysis_result = analyze_pushups_for_ai_suggestions(normalized_path)
            analysis_data = json.loads(analysis_result)
            
        except ImportError:
            logger.warning("Advanced AI analyzer not available, using simple AI")
            try:
                from simple_ai_analyzer import analyze_pushups_for_ai_suggestions_simple  # type: ignore
                analysis_result = analyze_pushups_for_ai_suggestions_simple(file_path)
                analysis_data = json.loads(analysis_result)
            except ImportError:
                logger.warning("Simple AI not available, using fallback")
                analysis_data = {
                    "exercise": "pushup",
                    "count": 8,
                    "form_score": 65,
                    "issues": ["form needs work", "inconsistent tempo"]
                }
        
        # Get improvement suggestions from Gemini
        try:
            from gemini_ai_service import generate_workout_suggestions
            suggestions = generate_workout_suggestions(analysis_data)
            
            # Combine analysis and suggestions
            complete_response = {
                "exercise_analysis": analysis_data,
                "improvement_suggestions": suggestions,
                "timestamp": timestamp,
                "filename": filename,
                "status": "success"
            }
            
            logger.info(f"Complete analysis and suggestions generated for: {filename}")
            return JSONResponse(content=complete_response)
            
        except Exception as gemini_error:
            logger.error(f"Gemini service error: {gemini_error}")
            # Return analysis without suggestions if Gemini fails
            fallback_response = {
                "exercise_analysis": analysis_data,
                "improvement_suggestions": {
                    "success": False,
                    "error": "AI suggestions service temporarily unavailable",
                    "message": "Exercise analysis completed, but improvement suggestions could not be generated."
                },
                "timestamp": timestamp,
                "filename": filename,
                "status": "partial_success"
            }
            
            return JSONResponse(content=fallback_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in improvement suggestions endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Profile and User Management Endpoints

@app.post("/dataset/upload")
async def upload_dataset_file(
    file: UploadFile = File(..., description="Labeled video to add to training dataset"),
    label: str = Form(..., description="Label for the video: 'correct' or 'wrong'"),
    overwrite: bool = Form(False, description="Overwrite if filename exists")
):
    """
    Upload a labeled video into the dataset folders used for training.
    Saves to data/correct or data/wrong based on 'label'.
    """
    try:
        # Validate label
        label_normalized = label.strip().lower()
        if label_normalized not in ("correct", "wrong"):
            raise HTTPException(status_code=422, detail="label must be 'correct' or 'wrong'")

        # Validate file provided
        if not file or not file.filename:
            raise HTTPException(status_code=422, detail="No file provided.")

        # Validate file extension
        allowed_extensions = (".mp4", ".avi", ".mov", ".mkv", ".webm")
        file_ext = os.path.splitext(file.filename.lower())[1]
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=422, detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")

        # Size guard (100MB)
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=422, detail="Uploaded file is empty.")
        if len(content) > 100 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 100MB.")

        # Ensure pointer reset before saving (good practice even after read())
        await file.seek(0)

        # Resolve destination path
        target_dir = DATA_CORRECT_DIR if label_normalized == "correct" else DATA_WRONG_DIR
        dest_path = os.path.join(target_dir, file.filename)

        # Handle overwrite or rename
        if os.path.exists(dest_path) and not overwrite:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(file.filename)
            dest_path = os.path.join(target_dir, f"{timestamp}_{name}{ext}")

        # Save file
        with open(dest_path, "wb") as f:
            f.write(await file.read())

        logger.info(f"Dataset file saved: {dest_path} (label={label_normalized})")
        return {
            "message": "Dataset file uploaded",
            "label": label_normalized,
            "destination": dest_path.replace("\\", "/")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dataset upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload dataset file")

@app.post("/dataset/retrain")
async def retrain_models():
    """
    Retrain the dataset-based models on files in data/correct and data/wrong.
    """
    try:
        if get_dataset_analyzer is None:
            raise HTTPException(status_code=500, detail="Training module not available")

        analyzer = get_dataset_analyzer()
        success = analyzer.train_models()
        if not success:
            raise HTTPException(status_code=400, detail="Insufficient or invalid training data")

        # Models are saved to disk and kept in-memory by the analyzer instance
        return {"message": "Retraining completed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Retraining error: {e}")
        raise HTTPException(status_code=500, detail="Retraining failed")

@app.post("/register")
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user_service = UserService(db)
        
        # Check if user already exists
        if user_service.get_user_by_username(user_data.username):
            raise HTTPException(status_code=400, detail="Username already registered")
        
        if user_service.get_user_by_email(user_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password (simplified - use proper hashing in production)
        hashed_password = f"hashed_{user_data.password}"  # TODO: Use bcrypt
        
        # Create user
        user = user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )
        
        return {
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/login")
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """User login"""
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_username(login_data.username)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Verify password (simplified - use proper verification in production)
        if user.hashed_password != f"hashed_{login_data.password}":
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        return {
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username,
            "access_token": f"token_{user.id}"  # TODO: Use proper JWT
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/profile/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Get user profile information"""
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            total_workouts=user.total_workouts,
            total_pushups=user.total_pushups,
            best_form_score=user.best_form_score,
            avg_form_score=user.avg_form_score,
            created_at=user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch profile")

@app.get("/me")
async def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Return the authenticated user's basic profile using the bearer token.
    Expects Authorization: Bearer token_<user_id> (temporary scheme).
    """
    try:
        user_id = verify_token(authorization)
        if not user_id:
            raise HTTPException(status_code=401, detail="Not authenticated")
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"/me endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch current user")

@app.get("/workouts/{user_id}")
async def get_user_workouts(user_id: int, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    """Get user's workout history"""
    try:
        workout_service = WorkoutService(db)
        workouts = workout_service.get_user_workouts(user_id, limit, offset)
        
        return {
            "workouts": [
                {
                    "id": w.id,
                    "exercise_type": w.exercise_type,
                    "pushup_count": w.pushup_count,
                    "duration_sec": w.duration_sec,
                    "form_score": w.form_score,
                    "avg_speed": w.avg_speed,
                    "total_distance": w.total_distance,
                    "ai_confidence": w.ai_confidence,
                    "model_used": w.model_used,
                    "video_filename": w.video_filename,
                    "analysis_notes": w.analysis_notes,
                    "created_at": w.created_at.isoformat(),
                    "processing_status": w.processing_status
                }
                for w in workouts
            ],
            "total_count": len(workouts),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Workout fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch workouts")

@app.get("/stats/{user_id}")
async def get_user_stats(user_id: int, days: int = 30, db: Session = Depends(get_db)):
    """Get user's workout statistics"""
    try:
        workout_service = WorkoutService(db)
        stats = workout_service.get_workout_stats(user_id, days)
        
        return {
            "user_id": user_id,
            "period_days": days,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Stats fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

@app.get("/progress/{user_id}")
async def get_user_progress(user_id: int, days: int = 30, db: Session = Depends(get_db)):
    """Get user's progress data for charts"""
    try:
        workout_service = WorkoutService(db)
        progress = workout_service.get_progress_data(user_id, days)
        
        return {
            "user_id": user_id,
            "period_days": days,
            "progress_data": progress
        }
        
    except Exception as e:
        logger.error(f"Progress fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch progress data")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)
