import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
import logging

# Database configuration
DATABASE_URL = "postgresql://neondb_owner:npg_QExrvh2uG8fb@ep-rapid-scene-adx4h7yq-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Create engine
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    total_workouts = Column(Integer, default=0)
    total_pushups = Column(Integer, default=0)
    best_form_score = Column(Float, default=0.0)
    avg_form_score = Column(Float, default=0.0)

class Workout(Base):
    __tablename__ = "workouts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Foreign key to users
    exercise_type = Column(String(50), nullable=False, default="pushup")
    pushup_count = Column(Integer, nullable=False)
    duration_sec = Column(Float, nullable=False)
    form_score = Column(Float, nullable=False)
    avg_speed = Column(Float)
    total_distance = Column(Float)
    ai_confidence = Column(Float)
    model_used = Column(String(100))
    video_filename = Column(String(255))
    analysis_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processing_status = Column(String(50), default="success")

class UserStats(Base):
    __tablename__ = "user_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Foreign key to users
    date = Column(DateTime(timezone=True), server_default=func.now())
    daily_pushups = Column(Integer, default=0)
    daily_workouts = Column(Integer, default=0)
    daily_avg_form = Column(Float, default=0.0)
    daily_total_time = Column(Float, default=0.0)
    best_single_workout = Column(Integer, default=0)

# Database helper functions
def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False

def test_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# Initialize database on import
if __name__ == "__main__":
    test_connection()
    create_tables()