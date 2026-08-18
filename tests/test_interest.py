"""
Unit tests for Multi-Reel Interest Inference and Built-in Trap Resolution.
"""

import pytest
from modules.interest_inference import InterestInferenceEngine
from modules.anomaly_detection import AnomalyDetector

@pytest.fixture
def hackathon_reels():
    return [
        {
            "reel_id": "REEL_001",
            "title": "Java Developer Debugging at 2 AM",
            "caption": "NullPointerException strikes again #java",
            "transcript": "Why is user null?",
            "category": "Java",
            "topic": "Java Debugging",
            "quality_score": 0.80
        },
        {
            "reel_id": "REEL_002",
            "title": "Day in the Life of a FAANG Software Engineer",
            "caption": "Standup at 10, code reviews, microservices architecture",
            "transcript": "Reviewing PRs and designing distributed queues.",
            "category": "Career",
            "topic": "SWE Lifestyle & Workflow",
            "quality_score": 0.85
        },
        {
            "reel_id": "REEL_003",
            "title": "Coding Interview: LeetCode Hard Reality Check",
            "caption": "Binary tree whiteboard interview #dsa",
            "transcript": "Inverting binary trees and detecting graph cycles.",
            "category": "DSA",
            "topic": "Technical Coding Interviews",
            "quality_score": 0.82
        },
        {
            "reel_id": "REEL_004",
            "title": "M3 Max MacBook Pro vs ThinkPad for Developers",
            "caption": "Docker compilation benchmarks side by side",
            "transcript": "Compiling large codebases and container performance.",
            "category": "Hardware",
            "topic": "Developer Workstations",
            "quality_score": 0.90
        }
    ]

def test_trap_resolution_infers_software_engineering(hackathon_reels):
    """
    CRITICAL HACKATHON TEST:
    A student watches Java meme, SWE lifestyle, Coding interview, and Laptop comparison.
    A shallow system infers Java.
    The AI system MUST infer Software Engineering as the primary underlying interest.
    """
    engine = InterestInferenceEngine()
    interactions = [
        {"reel_id": "REEL_001", "watch_percentage": 0.95, "liked": 1, "saved": 0, "shared": 0, "rewatched": 1, "skipped": 0, "engagement_score": 0.92},
        {"reel_id": "REEL_002", "watch_percentage": 1.00, "liked": 1, "saved": 1, "shared": 0, "rewatched": 0, "skipped": 0, "engagement_score": 0.98},
        {"reel_id": "REEL_003", "watch_percentage": 0.90, "liked": 1, "saved": 0, "shared": 0, "rewatched": 0, "skipped": 0, "engagement_score": 0.88},
        {"reel_id": "REEL_004", "watch_percentage": 0.85, "liked": 0, "saved": 1, "shared": 0, "rewatched": 0, "skipped": 0, "engagement_score": 0.84}
    ]

    result = engine.infer_interests(interactions, hackathon_reels)
    
    assert result["underlying_interest"] == "Software Engineering"
    assert "Software Engineering" in result["primary_interests"]
    assert result["interest_scores"]["Software Engineering"] >= 0.75
    # Java score should be secondary / lower than broader Software Engineering
    assert result["interest_scores"].get("Software Engineering", 0) > result["interest_scores"].get("Java", 0)
    assert len(result["evidence"]) >= 4

def test_cold_start_confidence():
    engine = InterestInferenceEngine()
    # 1 interaction only
    interactions = [{"reel_id": "REEL_001", "watch_percentage": 0.5, "liked": 0, "saved": 0, "shared": 0, "rewatched": 0, "skipped": 0, "engagement_score": 0.3}]
    catalog = [{"reel_id": "REEL_001", "title": "Test Reel", "category": "Java", "quality_score": 0.8}]
    
    result = engine.infer_interests(interactions, catalog)
    assert result["confidence"] == "Low"
    assert result["is_cold_start"] is True
