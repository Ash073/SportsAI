import cv2
import mediapipe as mp
import time

mp_pose = mp.solutions.pose

def analyze_pushups(video_path: str):
    cap = cv2.VideoCapture(video_path)
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    pushup_count = 0
    stage = None
    start_time = time.time()
    
    # Optional: distance/speed placeholders
    total_distance = 0
    prev_y = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Use landmarks: shoulder (11), elbow (13), wrist (15)
            left_shoulder = landmarks[11].y
            left_elbow = landmarks[13].y
            left_wrist = landmarks[15].y

            # Detect push-up stage (simple threshold)
            if left_elbow < left_shoulder and stage != "up":
                stage = "up"
            if left_elbow > left_shoulder and stage == "up":
                stage = "down"
                pushup_count += 1

            # Simple distance tracking for vertical motion
            if prev_y is not None:
                total_distance += abs(left_wrist - prev_y)
            prev_y = left_wrist

    end_time = time.time()
    duration = end_time - start_time  # seconds

    cap.release()
    pose.close()

    # Approximate speed (distance / time)
    speed = total_distance / duration if duration > 0 else 0

    return {
        "pushup_count": pushup_count,
        "duration_sec": round(duration, 2),
        "total_distance": round(total_distance, 4),
        "speed": round(speed, 4)
    }

