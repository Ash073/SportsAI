"""
Database Initialization and Test Data Setup
Run this script to set up initial data for testing the profile features
"""

from database import SessionLocal, User, Workout, create_tables, test_connection
from user_service import UserService, WorkoutService
from datetime import datetime, timedelta
import random

def create_test_user():
    """Create a test user for demonstration"""
    db = SessionLocal()
    try:
        user_service = UserService(db)
        
        # Check if test user already exists
        existing_user = user_service.get_user_by_username("testuser")
        if existing_user:
            print(f"Test user already exists with ID: {existing_user.id}")
            return existing_user.id
        
        # Create test user
        user = user_service.create_user(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password123",
            full_name="Test User"
        )
        
        print(f"Created test user with ID: {user.id}")
        return user.id
        
    except Exception as e:
        print(f"Error creating test user: {e}")
        return None
    finally:
        db.close()

def create_sample_workouts(user_id: int, num_workouts: int = 15):
    """Create sample workout data for testing"""
    db = SessionLocal()
    try:
        workout_service = WorkoutService(db)
        
        print(f"Creating {num_workouts} sample workouts...")
        
        for i in range(num_workouts):
            # Create varied workout data
            days_ago = random.randint(0, 30)
            workout_date = datetime.now() - timedelta(days=days_ago)
            
            # Simulate realistic workout data
            pushup_count = random.randint(5, 25)
            duration = random.uniform(30, 120)  # 30 seconds to 2 minutes
            form_score = random.uniform(4.0, 9.5)
            avg_speed = pushup_count / (duration / 60) if duration > 0 else 0
            
            analysis_result = {
                "pushup_count": pushup_count,
                "duration_sec": duration,
                "form_score": form_score,
                "avg_speed": avg_speed,
                "total_distance": pushup_count * 0.6,
                "ai_confidence": random.uniform(0.7, 0.95),
                "model_used": "Simple AI (RandomForest)" if i % 3 == 0 else "Advanced AI (MediaPipe)",
                "analysis_notes": [
                    "Good workout session",
                    "Consistent form maintained" if form_score > 7 else "Form needs improvement",
                    f"Completed {pushup_count} repetitions"
                ],
                "processing_status": "success"
            }
            
            # Create workout record
            workout = workout_service.save_workout(
                user_id=user_id,
                analysis_result=analysis_result,
                video_filename=f"test_workout_{i+1}.mp4"
            )
            
            # Set the created_at timestamp to simulate historical data
            workout.created_at = workout_date
            db.commit()
            
        print(f"Successfully created {num_workouts} sample workouts")
        
    except Exception as e:
        print(f"Error creating sample workouts: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main setup function"""
    print("Setting up Athlete's Edge AI Database...")
    
    # Test connection
    if not test_connection():
        print("Database connection failed. Please check your connection string.")
        return
    
    # Create tables
    create_tables()
    print("Database tables ready")
    
    # Create test user
    user_id = create_test_user()
    if not user_id:
        print("Failed to create test user")
        return
    
    # Create sample workouts
    create_sample_workouts(user_id, 15)
    
    print("\n" + "="*50)
    print("Database setup complete!")
    print(f"Test user ID: {user_id}")
    print("Username: testuser")
    print("Password: password123")
    print("="*50)
    print("\nYou can now:")
    print("1. Start the backend server: python app.py")
    print("2. Test the profile page with the test user")
    print("3. View workout history and statistics")

if __name__ == "__main__":
    main()