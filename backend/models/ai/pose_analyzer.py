import cv2
from load_models import load_pose_model
import numpy as np
import os
import json
import logging
import scipy.signal
import time
from typing import Dict, Any, Tuple, List

logger = logging.getLogger(__name__)

# Load the YOLO model once globally
try:
    pose_model = load_pose_model()
except Exception as e:
    logger.error(f"Failed to load YOLOv8 pose model: {e}")
    pose_model = None

def calculate_angle(a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
    """Calculate angle between three points (b is the vertex)"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    ba = a - b
    bc = c - b
    
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)
    
    if norm_ba == 0 or norm_bc == 0:
        return 0.0
        
    cosine_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    angle = np.degrees(np.arccos(cosine_angle))
    
    return float(angle)

def calculate_vector_angle(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    v1 = np.array(v1)
    v2 = np.array(v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    cosine = np.dot(v1, v2) / (norm1 * norm2)
    cosine = np.clip(cosine, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))

def interpolate_gaps(data: List[float], max_gap=5) -> List[float]:
    out = list(data)
    n = len(out)
    i = 0
    while i < n:
        if np.isnan(out[i]):
            start = i
            while i < n and np.isnan(out[i]):
                i += 1
            end = i
            gap_len = end - start
            if gap_len <= max_gap and start > 0 and end < n:
                val_start = out[start - 1]
                val_end = out[end]
                step = (val_end - val_start) / (gap_len + 1)
                for j in range(gap_len):
                    out[start + j] = val_start + step * (j + 1)
        else:
            i += 1
    return out

def fill_remaining_nans(data: List[float]) -> List[float]:
    """Forward fill then backward fill any remaining NaNs so savgol_filter doesn't crash."""
    out = list(data)
    n = len(out)
    
    # Forward fill
    last_valid = None
    for i in range(n):
        if not np.isnan(out[i]):
            last_valid = out[i]
        elif last_valid is not None:
            out[i] = last_valid
            
    # Backward fill
    last_valid = None
    for i in range(n-1, -1, -1):
        if not np.isnan(out[i]):
            last_valid = out[i]
        elif last_valid is not None:
            out[i] = last_valid
            
    # If all NaNs (shouldn't happen), return 0s
    for i in range(n):
        if np.isnan(out[i]):
            out[i] = 0.0
            
    return out

def analyze_video_with_pose(video_path: str) -> str:
    """
    Main function to analyze a pushup video using YOLOv8 Pose.
    Uses signal processing (savgol_filter + find_peaks) for accurate rep counting.
    """
    try:
        t0_start = time.time()
        
        if pose_model is None:
            return _build_error_response("YOLOv8 pose model not loaded", video_path)
            
        if not os.path.exists(video_path):
            return _build_error_response("Video file not found", video_path)

        t1_open = time.time()
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return _build_error_response("Could not open video file", video_path)
            
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_duration_sec = total_frames / fps if fps > 0 else 0
        
        # Calculate dynamic stride to target ~5 fps
        stride = max(1, round(fps / 5.0))
        
        # Raw metrics per sampled frame
        raw_elbow_angles = []
        raw_back_angles = []
        raw_flare_angles = []
        raw_sym_diffs = []
        
        frame_idx = 0
        person_detected_count = 0
        sampled_frames_count = 0
        
        t2_loop_start = time.time()
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_idx += 1
            
            # Enforce 20-second maximum duration cap
            current_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
            if current_msec > 20000:
                logger.warning(f"Video {video_path} truncated at 20 seconds for performance.")
                break
            
            # Sample every Nth frame based on dynamic stride
            if frame_idx % stride != 0:
                continue
                
            sampled_frames_count += 1
            
            # Downscale frame to max width of 480px for performance
            h, w = frame.shape[:2]
            if w > 480:
                scale = 480 / w
                new_w, new_h = 480, int(h * scale)
                frame = cv2.resize(frame, (new_w, new_h))
            
            # Run YOLOv8 inference with imgsz=256 for massive speedup
            results = pose_model(frame, imgsz=256, verbose=False)
            
            if not results or len(results[0].keypoints.data) == 0:
                raw_elbow_angles.append(np.nan)
                raw_back_angles.append(np.nan)
                raw_flare_angles.append(np.nan)
                raw_sym_diffs.append(np.nan)
                continue
                
            keypoints = results[0].keypoints.data[0].cpu().numpy()
            
            l_sh, r_sh = keypoints[5], keypoints[6]
            l_el, r_el = keypoints[7], keypoints[8]
            l_wr, r_wr = keypoints[9], keypoints[10]
            l_hip, r_hip = keypoints[11], keypoints[12]
            l_knee, r_knee = keypoints[13], keypoints[14]
            
            avg_visibility = (l_sh[2] + r_sh[2] + l_el[2] + r_el[2] + l_wr[2] + r_wr[2]) / 6.0
                                 
            if avg_visibility < 0.5:
                raw_elbow_angles.append(np.nan)
                raw_back_angles.append(np.nan)
                raw_flare_angles.append(np.nan)
                raw_sym_diffs.append(np.nan)
                continue
                
            person_detected_count += 1
            
            # Elbow angles
            l_elbow_angle = calculate_angle((l_sh[0], l_sh[1]), (l_el[0], l_el[1]), (l_wr[0], l_wr[1]))
            r_elbow_angle = calculate_angle((r_sh[0], r_sh[1]), (r_el[0], r_el[1]), (r_wr[0], r_wr[1]))
            avg_elbow_angle = (l_elbow_angle + r_elbow_angle) / 2.0
            
            # Back angles
            l_back_angle = calculate_angle((l_sh[0], l_sh[1]), (l_hip[0], l_hip[1]), (l_knee[0], l_knee[1]))
            r_back_angle = calculate_angle((r_sh[0], r_sh[1]), (r_hip[0], r_hip[1]), (r_knee[0], r_knee[1]))
            avg_back_angle = (l_back_angle + r_back_angle) / 2.0
            
            # Symmetry diff
            symmetry_diff = abs(l_elbow_angle - r_elbow_angle)
            
            # Flare angles
            l_v_torso = (l_hip[0] - l_sh[0], l_hip[1] - l_sh[1])
            l_v_arm = (l_el[0] - l_sh[0], l_el[1] - l_sh[1])
            l_flare = calculate_vector_angle(l_v_torso, l_v_arm)
            
            r_v_torso = (r_hip[0] - r_sh[0], r_hip[1] - r_sh[1])
            r_v_arm = (r_el[0] - r_sh[0], r_el[1] - r_sh[1])
            r_flare = calculate_vector_angle(r_v_torso, r_v_arm)
            
            avg_flare_angle = (l_flare + r_flare) / 2.0
            
            raw_elbow_angles.append(avg_elbow_angle)
            raw_back_angles.append(avg_back_angle)
            raw_flare_angles.append(avg_flare_angle)
            raw_sym_diffs.append(symmetry_diff)

        cap.release()
        t3_inference_done = time.time()
        
        # 30% visibility check
        if sampled_frames_count == 0 or (person_detected_count / sampled_frames_count) < 0.3:
            return _build_error_response("no person detected / poor video quality", video_path)
            
        # Interpolate gaps <= 5 (since stride is ~10fps, max 5 gaps = 0.5s)
        elbow_interp = interpolate_gaps(raw_elbow_angles, 5)
        back_interp = interpolate_gaps(raw_back_angles, 5)
        flare_interp = interpolate_gaps(raw_flare_angles, 5)
        sym_interp = interpolate_gaps(raw_sym_diffs, 5)
        
        # Fill remaining NaNs to prevent savgol_filter crash
        elbow_filled = fill_remaining_nans(elbow_interp)
        back_filled = fill_remaining_nans(back_interp)
        flare_filled = fill_remaining_nans(flare_interp)
        sym_filled = fill_remaining_nans(sym_interp)
        
        # Smooth elbow signal
        window_len = min(7, len(elbow_filled))
        if window_len % 2 == 0:
            window_len -= 1
            
        if window_len >= 3:
            smoothed_elbow = scipy.signal.savgol_filter(elbow_filled, window_len, 2)
        else:
            smoothed_elbow = np.array(elbow_filled)
            
        # Find pushup valleys (peaks in negative signal)
        # distance = min expected frames between reps. Sampled every 2 frames -> fps/2 = 1 sec. fps/4 = 0.5s.
        min_distance = max(1, int(fps / 4.0)) 
        valleys, _ = scipy.signal.find_peaks(-smoothed_elbow, distance=min_distance, prominence=20)
        
        # Find all local maxima (lockouts)
        lockouts, _ = scipy.signal.find_peaks(smoothed_elbow, distance=min_distance, prominence=15)
        
        rep_count = len(valleys)
        per_rep_detail = []
        
        flags_triggered = {
            "insufficient_depth": 0,
            "hips_sagging": 0,
            "hips_high": 0,
            "elbows_flaring": 0,
            "incomplete_lockout": 0,
            "uneven_push": 0
        }
        
        for v_idx in valleys:
            # find closest lockout before and after
            before_lockouts = [l for l in lockouts if l < v_idx]
            after_lockouts = [l for l in lockouts if l > v_idx]
            
            lockout_b = smoothed_elbow[before_lockouts[-1]] if before_lockouts else smoothed_elbow[v_idx]
            lockout_a = smoothed_elbow[after_lockouts[0]] if after_lockouts else smoothed_elbow[v_idx]
            
            depth = smoothed_elbow[v_idx]
            lockout = max(lockout_b, lockout_a)
            back = back_filled[v_idx]
            flare = flare_filled[v_idx]
            sym = sym_filled[v_idx]
            
            if depth > 100.0: flags_triggered["insufficient_depth"] += 1
            if back < 160.0: flags_triggered["hips_sagging"] += 1
            if back > 185.0: flags_triggered["hips_high"] += 1
            if flare > 60.0: flags_triggered["elbows_flaring"] += 1
            if lockout < 160.0: flags_triggered["incomplete_lockout"] += 1
            if sym > 15.0: flags_triggered["uneven_push"] += 1
            
            per_rep_detail.append({
                "rep": len(per_rep_detail) + 1,
                "depth_angle": round(float(depth), 1),
                "lockout_angle": round(float(lockout), 1),
                "back_angle": round(float(back), 1),
                "elbow_flare_angle": round(float(flare), 1),
                "left_right_diff": round(float(sym), 1)
            })

        feedback = []
        form_score = 10.0
        threshold = rep_count / 2.0 if rep_count > 0 else 0

        if rep_count > 0:
            if flags_triggered["insufficient_depth"] > threshold:
                feedback.append(f"insufficient depth on {flags_triggered['insufficient_depth']} of {rep_count} reps")
                form_score -= 2.0
            if flags_triggered["hips_sagging"] > threshold:
                feedback.append(f"hips sagging on {flags_triggered['hips_sagging']} of {rep_count} reps")
                form_score -= 1.5
            if flags_triggered["hips_high"] > threshold:
                feedback.append(f"hips too high on {flags_triggered['hips_high']} of {rep_count} reps")
                form_score -= 1.5
            if flags_triggered["elbows_flaring"] > threshold:
                feedback.append(f"elbows flaring out on {flags_triggered['elbows_flaring']} of {rep_count} reps")
                form_score -= 1.0
            if flags_triggered["incomplete_lockout"] > threshold:
                feedback.append(f"incomplete lockout at top on {flags_triggered['incomplete_lockout']} of {rep_count} reps")
                form_score -= 1.5
            if flags_triggered["uneven_push"] > threshold:
                feedback.append(f"uneven left/right push on {flags_triggered['uneven_push']} of {rep_count} reps")
                form_score -= 1.0
                
            form_score = max(0.0, round(form_score, 1))
            
            if form_score == 10.0:
                feedback.append("Excellent form on all reps!")
        else:
            form_score = 0.0
            feedback.append("No valid reps detected.")

        t4_processing_done = time.time()
        
        analysis_duration = t4_processing_done - t0_start
        actual_video_duration = min(20.0, video_duration_sec) if video_duration_sec > 20 else video_duration_sec
        
        # Log timing
        logger.info(f"[TIMING] Total time: {analysis_duration:.2f}s | " 
                    f"Init: {t1_open - t0_start:.2f}s | "
                    f"YOLO Inference ({sampled_frames_count} frames): {t3_inference_done - t2_loop_start:.2f}s | "
                    f"Signal Processing: {t4_processing_done - t3_inference_done:.2f}s")

        # Construct final response (backward compatible but extended)
        result = {
            "pushup_count": rep_count,
            "rep_count": rep_count,
            "duration_sec": round(actual_video_duration, 1),
            "total_distance": round(rep_count * 0.6, 2),
            "avg_speed": round(rep_count / (actual_video_duration / 60), 2) if actual_video_duration > 0 else 0,
            "form_score": form_score,
            "feedback": feedback,
            "analysis_notes": feedback,
            "per_rep_detail": per_rep_detail,
            "video_processed": os.path.basename(video_path),
            "processing_status": "success_pose_analyzer",
            "ai_confidence": round(person_detected_count / sampled_frames_count, 2) if sampled_frames_count > 0 else 0,
            "model_used": "YOLOv8 Pose (Optimized)",
            "form_breakdown": {
                "back_alignment": max(0, 10.0 - (flags_triggered["hips_sagging"]*1.5 + flags_triggered["hips_high"]*1.5)),
                "depth_consistency": max(0, 10.0 - flags_triggered["insufficient_depth"]*2.0),
                "symmetry": max(0, 10.0 - flags_triggered["uneven_push"]*1.0)
            }
        }
        
        return json.dumps(result)
        
    except Exception as e:
        logger.error(f"Error in pose_analyzer: {str(e)}")
        return _build_error_response(f"Analysis failed: {str(e)}", video_path)

def _build_error_response(msg: str, video_path: str) -> str:
    return json.dumps({
        "error": msg,
        "pushup_count": 0,
        "rep_count": 0,
        "duration_sec": 0,
        "total_distance": 0,
        "avg_speed": 0,
        "form_score": 0,
        "feedback": [msg],
        "analysis_notes": [msg],
        "per_rep_detail": [],
        "video_processed": os.path.basename(video_path) if video_path else "unknown",
        "processing_status": "error",
        "ai_confidence": 0.0,
        "model_used": "YOLOv8 Pose"
    })
