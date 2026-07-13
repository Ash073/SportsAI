import os
import joblib
import logging
from typing import Optional, Any
from ultralytics import YOLO  # type: ignore

logger = logging.getLogger(__name__)

# Base directory for models
MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
FROZEN_DIR = os.path.join(MODELS_DIR, 'frozen')
LEGACY_DIR = os.path.join(MODELS_DIR, 'legacy')

# Lazy loaded singletons
_pose_model = None
_pushup_count_model = None
_pushup_form_model = None
_feature_scaler = None

def load_pose_model() -> Optional[Any]:
    global _pose_model
    if _pose_model is None:
        model_path = os.path.join(FROZEN_DIR, "yolov8n-pose.pt")
        try:
            _pose_model = YOLO(model_path)
            logger.info(f"Successfully loaded YOLOv8 pose model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load YOLOv8 pose model: {e}")
    return _pose_model

def load_pushup_count_model() -> Optional[Any]:
    global _pushup_count_model
    if _pushup_count_model is None:
        model_path = os.path.join(FROZEN_DIR, "pushup_count_model.joblib")
        try:
            _pushup_count_model = joblib.load(model_path)
            logger.info(f"Successfully loaded pushup count model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load pushup count model: {e}")
    return _pushup_count_model

def load_pushup_form_model() -> Optional[Any]:
    global _pushup_form_model
    if _pushup_form_model is None:
        model_path = os.path.join(FROZEN_DIR, "pushup_form_model.joblib")
        try:
            _pushup_form_model = joblib.load(model_path)
            logger.info(f"Successfully loaded pushup form model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load pushup form model: {e}")
    return _pushup_form_model

def load_feature_scaler() -> Optional[Any]:
    global _feature_scaler
    if _feature_scaler is None:
        model_path = os.path.join(FROZEN_DIR, "feature_scaler.joblib")
        try:
            _feature_scaler = joblib.load(model_path)
            logger.info(f"Successfully loaded feature scaler from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load feature scaler: {e}")
    return _feature_scaler
