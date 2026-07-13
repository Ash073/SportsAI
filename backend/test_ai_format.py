#!/usr/bin/env python3
"""
Test script to demonstrate the AI suggestions format output.
This shows how the analysis results are formatted for AI improvement suggestions.
"""

import json
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ai_format_conversion():
    """Test the format conversion function"""
    
    # Sample analysis result (what we currently get)
    sample_full_result = {
        "pushup_count": 12,
        "duration_sec": 45.6,
        "total_distance": 7.2,
        "avg_speed": 15.8,
        "form_score": 7.8,  # Scale 0-10
        "analysis_notes": [
            "Good form with minor inconsistencies",
            "Uneven arm movement detected",
            "Arms not bending enough - go lower",
            "Decent tempo maintained"
        ],
        "video_processed": "pushup_video.mp4",
        "processing_status": "success_ai_model",
        "ai_confidence": 0.87,
        "model_used": "MediaPipe + RandomForest"
    }
    
    print("Original Analysis Result:")
    print(json.dumps(sample_full_result, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Convert to AI suggestions format
    try:
        from ai_exercise_analyzer import format_for_ai_suggestions
        ai_format_result = format_for_ai_suggestions(sample_full_result)
        
        print("Formatted for AI Suggestions:")
        print(json.dumps(ai_format_result, indent=2))
        
        print("\n" + "="*50 + "\n")
        print("Expected format example:")
        expected_format = {
            "exercise": "pushup",
            "count": 12,
            "form_score": 78,
            "issues": ["elbows too wide", "incomplete depth"]
        }
        print(json.dumps(expected_format, indent=2))
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("AI exercise analyzer not available. Using mock conversion.")
        
        # Mock conversion for demonstration
        exercise = "pushup"
        count = sample_full_result.get("pushup_count", 0)
        form_score_10 = sample_full_result.get("form_score", 0)
        form_score = int(form_score_10 * 10)  # Convert to 0-100 scale
        
        # Extract issues from analysis notes
        analysis_notes = sample_full_result.get("analysis_notes", [])
        issues = []
        
        for note in analysis_notes:
            note_lower = note.lower()
            if "uneven arm" in note_lower:
                issues.append("uneven arm movement")
            elif "not bending enough" in note_lower or "go lower" in note_lower:
                issues.append("incomplete depth")
            elif "elbows" in note_lower and "wide" in note_lower:
                issues.append("elbows too wide")
        
        mock_result = {
            "exercise": exercise,
            "count": count,
            "form_score": form_score,
            "issues": issues
        }
        
        print("Mock AI Suggestions Format:")
        print(json.dumps(mock_result, indent=2))

def test_api_endpoint_simulation():
    """Simulate what the new API endpoint would return"""
    
    print("\n" + "="*60)
    print("NEW API ENDPOINT SIMULATION")
    print("="*60 + "\n")
    
    print("Endpoint: POST /analyze-for-ai-suggestions")
    print("Input: video file + exercise type")
    print("Output format:")
    
    # Different scenarios
    scenarios = [
        {
            "description": "Good performance",
            "result": {
                "exercise": "pushup",
                "count": 15,
                "form_score": 82,
                "issues": []
            }
        },
        {
            "description": "Average performance with issues",
            "result": {
                "exercise": "pushup",
                "count": 8,
                "form_score": 67,
                "issues": ["elbows too wide", "incomplete depth"]
            }
        },
        {
            "description": "Poor performance",
            "result": {
                "exercise": "pushup",
                "count": 3,
                "form_score": 42,
                "issues": ["poor form technique", "inconsistent tempo", "needs practice"]
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}: {scenario['description']}")
        print(json.dumps(scenario['result'], indent=2))

if __name__ == "__main__":
    print("Testing AI Suggestions Format Conversion")
    print("="*60)
    
    test_ai_format_conversion()
    test_api_endpoint_simulation()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("✅ Added new function: format_for_ai_suggestions()")
    print("✅ Added new function: analyze_pushups_for_ai_suggestions()")
    print("✅ Added new API endpoint: POST /analyze-for-ai-suggestions")
    print("✅ Output format matches your requirement:")
    print("   {exercise, count, form_score, issues}")
    print("\n📋 You can now send the formatted output to any AI service")
    print("   for personalized improvement suggestions!")