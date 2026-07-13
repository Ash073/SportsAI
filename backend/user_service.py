from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
import logging
from database import User, Workout, UserStats

logger = logging.getLogger(__name__)

class UserService:
    """Service for user-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, username: str, email: str, hashed_password: str, full_name: Optional[str] = None) -> User:
        """Create a new user"""
        try:
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                full_name=full_name
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"Created new user: {username}")
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user {username}: {e}")
            raise
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update_user_stats(self, user_id: int, workout: Workout):
        """Update user's overall statistics after a workout"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return
            
            # Update totals
            user.total_workouts += 1
            user.total_pushups += workout.pushup_count
            
            # Update best form score
            if workout.form_score > user.best_form_score:
                user.best_form_score = workout.form_score
            
            # Calculate new average form score
            avg_query = self.db.query(func.avg(Workout.form_score)).filter(Workout.user_id == user_id)
            new_avg = avg_query.scalar() or 0.0
            user.avg_form_score = round(new_avg, 2)
            
            self.db.commit()
            logger.info(f"Updated stats for user {user_id}")
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating user stats for {user_id}: {e}")
            raise

class WorkoutService:
    """Service for workout-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_workout(self, user_id: int, analysis_result: Dict[str, Any], video_filename: Optional[str] = None) -> Workout:
        """Save workout analysis results to database"""
        try:
            workout = Workout(
                user_id=user_id,
                exercise_type="pushup",
                pushup_count=analysis_result.get("pushup_count", 0),
                duration_sec=analysis_result.get("duration_sec", 0.0),
                form_score=analysis_result.get("form_score", 0.0),
                avg_speed=analysis_result.get("avg_speed", 0.0),
                total_distance=analysis_result.get("total_distance", 0.0),
                ai_confidence=analysis_result.get("ai_confidence", 0.0),
                model_used=analysis_result.get("model_used", "Unknown"),
                video_filename=video_filename,
                analysis_notes=str(analysis_result.get("analysis_notes", [])),
                processing_status=analysis_result.get("processing_status", "success")
            )
            
            self.db.add(workout)
            self.db.commit()
            self.db.refresh(workout)
            
            # Update user stats
            user_service = UserService(self.db)
            user_service.update_user_stats(user_id, workout)
            
            logger.info(f"Saved workout for user {user_id}")
            return workout
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving workout for user {user_id}: {e}")
            raise
    
    def get_user_workouts(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Workout]:
        """Get user's workout history"""
        return (self.db.query(Workout)
                .filter(Workout.user_id == user_id)
                .order_by(desc(Workout.created_at))
                .offset(offset)
                .limit(limit)
                .all())
    
    def get_workout_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get workout statistics for the last N days"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Get workouts in the time period
            workouts = (self.db.query(Workout)
                       .filter(and_(Workout.user_id == user_id, 
                                  Workout.created_at >= start_date))
                       .all())
            
            if not workouts:
                return {
                    "total_workouts": 0,
                    "total_pushups": 0,
                    "avg_form_score": 0.0,
                    "best_form_score": 0.0,
                    "total_time": 0.0,
                    "avg_workout_time": 0.0,
                    "days_active": 0,
                    "daily_breakdown": []
                }
            
            # Calculate statistics
            total_workouts = len(workouts)
            total_pushups = sum(w.pushup_count for w in workouts)
            avg_form_score = sum(w.form_score for w in workouts) / total_workouts
            best_form_score = max(w.form_score for w in workouts)
            total_time = sum(w.duration_sec for w in workouts)
            avg_workout_time = total_time / total_workouts
            
            # Days active
            unique_dates = set(w.created_at.date() for w in workouts)
            days_active = len(unique_dates)
            
            # Daily breakdown
            daily_stats = {}
            for workout in workouts:
                day = workout.created_at.date()
                if day not in daily_stats:
                    daily_stats[day] = {
                        "date": day.isoformat(),
                        "workouts": 0,
                        "pushups": 0,
                        "avg_form": 0.0,
                        "total_time": 0.0,
                        "form_scores": []
                    }
                daily_stats[day]["workouts"] += 1
                daily_stats[day]["pushups"] += workout.pushup_count
                daily_stats[day]["total_time"] += workout.duration_sec
                daily_stats[day]["form_scores"].append(workout.form_score)
            
            # Calculate daily averages
            for day_data in daily_stats.values():
                if day_data["form_scores"]:
                    day_data["avg_form"] = sum(day_data["form_scores"]) / len(day_data["form_scores"])
                del day_data["form_scores"]  # Remove raw scores
            
            return {
                "total_workouts": total_workouts,
                "total_pushups": total_pushups,
                "avg_form_score": round(avg_form_score, 2),
                "best_form_score": round(best_form_score, 2),
                "total_time": round(total_time, 1),
                "avg_workout_time": round(avg_workout_time, 1),
                "days_active": days_active,
                "daily_breakdown": sorted(daily_stats.values(), 
                                        key=lambda x: x["date"], reverse=True)
            }
            
        except Exception as e:
            logger.error(f"Error calculating workout stats for user {user_id}: {e}")
            return {}
    
    def get_progress_data(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get progress data for charts and trends"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            workouts = (self.db.query(Workout)
                       .filter(and_(Workout.user_id == user_id,
                                  Workout.created_at >= start_date))
                       .order_by(Workout.created_at)
                       .all())
            
            if not workouts:
                return {"form_progress": [], "volume_progress": [], "consistency": []}
            
            # Group by date for trend analysis
            daily_data = {}
            for workout in workouts:
                day = workout.created_at.date().isoformat()
                if day not in daily_data:
                    daily_data[day] = {
                        "date": day,
                        "pushups": 0,
                        "workouts": 0,
                        "form_scores": [],
                        "total_time": 0.0
                    }
                daily_data[day]["pushups"] += workout.pushup_count
                daily_data[day]["workouts"] += 1
                daily_data[day]["form_scores"].append(workout.form_score)
                daily_data[day]["total_time"] += workout.duration_sec
            
            # Calculate trends
            form_progress = []
            volume_progress = []
            consistency = []
            
            for day, data in sorted(daily_data.items()):
                avg_form = sum(data["form_scores"]) / len(data["form_scores"])
                form_progress.append({"date": day, "value": round(avg_form, 2)})
                volume_progress.append({"date": day, "value": data["pushups"]})
                consistency.append({"date": day, "value": data["workouts"]})
            
            return {
                "form_progress": form_progress,
                "volume_progress": volume_progress,
                "consistency": consistency
            }
            
        except Exception as e:
            logger.error(f"Error getting progress data for user {user_id}: {e}")
            return {"form_progress": [], "volume_progress": [], "consistency": []}