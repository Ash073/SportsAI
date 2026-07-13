"""
Real Video Analysis using OpenCV
This replaces all mock analysis with actual video processing
"""

import cv2
import numpy as np
import json
import logging
import os
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class RealVideoAnalyzer:
    """Real video analyzer that processes actual video frames"""
    
    def __init__(self):
        self.motion_threshold = 500   # Reduced threshold for better sensitivity
        self.min_pushup_frames = 10   # Reduced minimum frames
        self.max_pushup_frames = 150  # Increased maximum frames
        
    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """Main video analysis function"""
        
        try:
            logger.info(f"Starting REAL video analysis of: {os.path.basename(video_path)}")
            
            # Check if OpenCV can open the video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise Exception(f"Cannot open video file: {video_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS) or 25  # Default to 25 fps if unknown
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            logger.info(f"Video properties: {frame_count} frames, {fps:.1f} fps, {duration:.1f}s")
            
            # Analyze motion patterns
            motion_data = self.extract_motion_patterns(cap)
            cap.release()
            
            # Count pushups from motion patterns
            pushup_count = self.count_pushups_from_motion(motion_data, fps)
            
            # Calculate form score
            form_score = self.calculate_form_score(motion_data, pushup_count)
            
            # Generate analysis notes
            analysis_notes = self.generate_analysis_notes(pushup_count, form_score, motion_data, duration)
            
            # Calculate other metrics
            avg_speed = (pushup_count / (duration / 60)) if duration > 0 else 0
            total_distance = pushup_count * 0.6  # Approximate distance per pushup
            
            # Calculate confidence based on motion quality
            ai_confidence = self.calculate_confidence(motion_data, pushup_count)
            
            results = {
                "pushup_count": int(pushup_count),
                "duration_sec": round(duration, 1),
                "total_distance": round(total_distance, 2),
                "avg_speed": round(avg_speed, 2),
                "form_score": round(form_score, 1),
                "analysis_notes": analysis_notes,
                "video_processed": os.path.basename(video_path),
                "processing_status": "success_real_video_analysis",
                "ai_confidence": round(ai_confidence, 3),
                "model_used": "Real OpenCV Video Analysis",
                "motion_frames_analyzed": len(motion_data.get('motion_values', [])),
                "fps": round(fps, 1),
                "frame_count": frame_count
            }
            
            logger.info(f"Real video analysis completed: {pushup_count} pushups, {form_score:.1f} form score")
            return results
            
        except Exception as e:
            logger.error(f"Real video analysis failed: {e}")
            raise e
    
    def extract_motion_patterns(self, cap) -> Dict[str, Any]:
        """Extract motion patterns from video frames"""
        
        motion_values = []
        prev_gray = None
        frame_index = 0
        motion_peaks = []
        
        # Reset video to beginning
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to grayscale and resize for faster processing
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (320, 240))  # Smaller size for faster processing
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            if prev_gray is not None:
                # Calculate frame difference (motion detection)
                frame_diff = cv2.absdiff(prev_gray, gray)
                _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
                
                # Count motion pixels
                motion_pixels = cv2.countNonZero(thresh)
                
                # Normalize motion by frame size
                frame_area = gray.shape[0] * gray.shape[1]
                motion_intensity = motion_pixels / frame_area
                
                motion_values.append(motion_intensity)
                
                # Detect motion peaks (potential pushup positions)
                if len(motion_values) >= 5:
                    recent_motion = motion_values[-5:]
                    current_motion = recent_motion[-1]
                    
                    # Check if current frame is a local maximum
                    if (current_motion > self.motion_threshold / frame_area and
                        current_motion == max(recent_motion)):
                        
                        # Avoid duplicate peaks too close together
                        if not motion_peaks or (frame_index - motion_peaks[-1]) > 10:
                            motion_peaks.append(frame_index)
            
            prev_gray = gray
            frame_index += 1
            
            # Process every frame for accuracy, but can be optimized
            
        return {
            'motion_values': motion_values,
            'motion_peaks': motion_peaks,
            'total_frames': frame_index,
            'avg_motion': np.mean(motion_values) if motion_values else 0,
            'max_motion': max(motion_values) if motion_values else 0,
            'motion_variance': np.var(motion_values) if motion_values else 0
        }
    
    def count_pushups_from_motion(self, motion_data: Dict, fps: float) -> int:
        """Count pushups based on real motion analysis"""
        
        motion_values = motion_data.get('motion_values', [])
        motion_peaks = motion_data.get('motion_peaks', [])
        
        if not motion_values or len(motion_values) < 30:
            logger.warning("Insufficient motion data for analysis")
            return 0
        
        # Smooth the motion data to reduce noise
        smoothed_motion = self.smooth_motion_data(motion_values)
        
        # Find pushup cycles using motion patterns
        pushup_cycles = self.detect_pushup_cycles(smoothed_motion, fps)
        
        # Validate cycles (remove false positives)
        valid_cycles = self.validate_pushup_cycles(pushup_cycles, smoothed_motion, fps)
        
        pushup_count = len(valid_cycles)
        
        logger.info(f"Motion analysis: {len(motion_peaks)} peaks detected, {len(pushup_cycles)} cycles found, {pushup_count} valid pushups")
        
        return pushup_count
    
    def smooth_motion_data(self, motion_values: List[float], window_size: int = 5) -> List[float]:
        """Apply moving average to smooth motion data"""
        
        if len(motion_values) < window_size:
            return motion_values
        
        smoothed = []
        for i in range(len(motion_values)):
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(motion_values), i + window_size // 2 + 1)
            window_avg = sum(motion_values[start_idx:end_idx]) / (end_idx - start_idx)
            smoothed.append(window_avg)
        
        return smoothed
    
    def detect_pushup_cycles(self, motion_values: List[float], fps: float) -> List[Dict]:
        """Detect pushup cycles from motion data"""
        
        cycles = []
        min_cycle_frames = int(fps * 1.0)  # Minimum 1 second per pushup
        max_cycle_frames = int(fps * 6.0)  # Maximum 6 seconds per pushup
        
        # Find peaks and valleys in motion
        peaks = []
        valleys = []
        
        for i in range(1, len(motion_values) - 1):
            if (motion_values[i] > motion_values[i-1] and 
                motion_values[i] > motion_values[i+1] and
                motion_values[i] > np.mean(motion_values) * 0.8):  # Reduced threshold from 1.2 to 0.8
                peaks.append(i)
            elif (motion_values[i] < motion_values[i-1] and 
                  motion_values[i] < motion_values[i+1] and
                  motion_values[i] < np.mean(motion_values) * 1.2):  # Increased threshold from 0.8 to 1.2
                valleys.append(i)
        
        # Match peaks with valleys to form cycles
        for peak in peaks:
            # Find nearest valleys before and after peak
            before_valleys = [v for v in valleys if v < peak]
            after_valleys = [v for v in valleys if v > peak]
            
            if before_valleys and after_valleys:
                start_valley = max(before_valleys)
                end_valley = min(after_valleys)
                
                cycle_length = end_valley - start_valley
                
                if min_cycle_frames <= cycle_length <= max_cycle_frames:
                    cycles.append({
                        'start': start_valley,
                        'peak': peak,
                        'end': end_valley,
                        'length': cycle_length,
                        'motion_range': motion_values[peak] - min(motion_values[start_valley], motion_values[end_valley])
                    })
        
        return cycles
    
    def validate_pushup_cycles(self, cycles: List[Dict], motion_values: List[float], fps: float) -> List[Dict]:
        """Validate detected cycles to remove false positives"""
        
        valid_cycles = []
        min_separation = int(fps * 0.5)  # Minimum 0.5 seconds between pushups
        
        for cycle in cycles:
            # Check motion range (pushup should have significant motion change)
            if cycle['motion_range'] < np.std(motion_values) * 0.5:
                continue
            
            # Check if too close to previous valid cycle
            if valid_cycles:
                last_cycle = valid_cycles[-1]  
                if cycle['start'] - last_cycle['end'] < min_separation:
                    continue
            
            # Check cycle shape (should have clear up and down motion)
            cycle_motion = motion_values[cycle['start']:cycle['end']]
            if len(cycle_motion) < 10:
                continue
            
            # Cycle should have a clear peak in the middle portion
            peak_position = cycle['peak'] - cycle['start']
            cycle_length = cycle['end'] - cycle['start']
            
            if not (0.2 * cycle_length <= peak_position <= 0.8 * cycle_length):
                continue
            
            valid_cycles.append(cycle)
        
        return valid_cycles
    
    def calculate_form_score(self, motion_data: Dict, pushup_count: int) -> float:
        """Calculate form score based on motion consistency"""
        
        motion_values = motion_data.get('motion_values', [])
        if not motion_values:
            return 1.0
        
        # Motion consistency (lower variance = better form)
        motion_variance = motion_data.get('motion_variance', 0)
        avg_motion = motion_data.get('avg_motion', 0)
        
        consistency_score = 1.0
        if avg_motion > 0:
            consistency_score = max(0.0, 1.0 - (motion_variance / avg_motion))
        
        # Movement smoothness
        smoothness_score = 0.8  # Base score
        if len(motion_values) > 10:
            # Calculate how smooth the motion is
            motion_changes = [abs(motion_values[i] - motion_values[i-1]) 
                            for i in range(1, len(motion_values))]
            avg_change = np.mean(motion_changes)
            if avg_change < np.std(motion_values):
                smoothness_score = 0.9
        
        # Pushup completion rate
        completion_score = 1.0
        if pushup_count == 0:
            completion_score = 0.3
        elif pushup_count < 3:
            completion_score = 0.6
        
        # Combine scores
        combined_score = (consistency_score * 0.4 + smoothness_score * 0.3 + completion_score * 0.3)
        
        # Convert to 1-10 scale
        form_score = 1.0 + (combined_score * 9.0)
        
        return form_score
    
    def calculate_confidence(self, motion_data: Dict, pushup_count: int) -> float:
        """Calculate confidence in the analysis"""
        
        motion_values = motion_data.get('motion_values', [])
        
        if not motion_values:
            return 0.1
        
        # Data quality score
        data_quality = min(1.0, len(motion_values) / 100)  # More frames = better
        
        # Motion detection quality
        avg_motion = motion_data.get('avg_motion', 0)
        motion_quality = min(1.0, avg_motion * 1000)  # Scale up small values
        
        # Result reasonableness
        result_quality = 1.0
        if pushup_count > 50 or pushup_count < 0:  # Unreasonable counts
            result_quality = 0.3
        elif pushup_count == 0:
            result_quality = 0.5
        
        return (data_quality * 0.3 + motion_quality * 0.4 + result_quality * 0.3)
    
    def generate_analysis_notes(self, pushup_count: int, form_score: float, 
                              motion_data: Dict, duration: float) -> List[str]:
        """Generate analysis notes based on actual video analysis"""
        
        notes = []
        
        # Count-based feedback
        if pushup_count == 0:
            notes.append("No pushups detected - ensure full body is visible and exercise is performed clearly")
        elif pushup_count == 1:
            notes.append("Single pushup detected - great start!")
        elif pushup_count < 5:
            notes.append(f"{pushup_count} pushups completed - good effort, keep building strength")
        elif pushup_count >= 10:
            notes.append(f"Excellent performance with {pushup_count} pushups!")
        else:
            notes.append(f"{pushup_count} pushups completed - solid workout")
        
        # Form feedback
        if form_score >= 8.5:
            notes.append("Excellent form consistency throughout the exercise")
        elif form_score >= 7.0:
            notes.append("Good form with consistent movement patterns")
        elif form_score >= 5.0:
            notes.append("Moderate form - focus on smooth, controlled movements")
        else:
            notes.append("Form needs improvement - work on movement consistency")
        
        # Motion analysis feedback
        avg_motion = motion_data.get('avg_motion', 0)
        if avg_motion < 0.01:
            notes.append("Low motion detected - ensure camera captures full range of movement")
        elif avg_motion > 0.05:
            notes.append("Good range of motion detected")
        
        # Duration feedback
        if duration < 10:
            notes.append("Short workout duration - consider longer sessions for better results")
        elif duration > 60:
            notes.append("Long workout session - excellent endurance!")
        
        return notes

# Global analyzer instance
real_analyzer = None

def get_real_analyzer() -> RealVideoAnalyzer:
    """Get or create the real analyzer instance"""
    global real_analyzer
    if real_analyzer is None:
        real_analyzer = RealVideoAnalyzer()
    return real_analyzer

def analyze_video_real(video_path: str) -> str:
    """Main function for real video analysis"""
    
    try:
        analyzer = get_real_analyzer()
        results = analyzer.analyze_video(video_path)
        return json.dumps(results)
        
    except Exception as e:
        logger.error(f"Real video analysis failed: {e}")
        return json.dumps({
            "error": f"Real video analysis failed: {str(e)}",
            "pushup_count": 0,
            "duration_sec": 0,
            "total_distance": 0,
            "avg_speed": 0,
            "form_score": 0,
            "analysis_notes": ["Real video analysis failed - check video format and content"]
        })

if __name__ == "__main__":
    # Test the real analyzer
    print("Testing Real Video Analyzer...")
    
    test_videos = [
        "uploads/20250923_213205_Copy of push up 3.mp4",
        "uploads/Copy of push up 4.mp4"
    ]
    
    for video_path in test_videos:
        if os.path.exists(video_path):
            print(f"\nTesting with: {video_path}")
            try:
                result = analyze_video_real(video_path)
                result_dict = json.loads(result)
                print(f"Pushups detected: {result_dict.get('pushup_count', 'N/A')}")
                print(f"Form score: {result_dict.get('form_score', 'N/A')}")
                print(f"Processing status: {result_dict.get('processing_status', 'N/A')}")
            except Exception as e:
                print(f"Error: {e}")
            break
    else:
        print("No test videos found")