"""
Unit tests for Behavior Analysis and Engagement Scoring.
"""

import pytest
from modules.behavior_analysis import BehaviorAnalysis
from utils.scoring import calculate_engagement_score

def test_engagement_score_high_positive():
    score = calculate_engagement_score(
        watch_percentage=1.0,
        liked=True,
        saved=True,
        shared=False,
        rewatched=True,
        skipped=False
    )
    # 0.40*1.0 + 0.20 + 0.20 + 0.10 = 0.90
    assert score >= 0.85
    assert score <= 1.0

def test_engagement_score_immediate_skip():
    score = calculate_engagement_score(
        watch_percentage=0.05,
        liked=False,
        saved=False,
        shared=False,
        rewatched=False,
        skipped=True
    )
    # 0.4*0.05 - 0.30 = max(0, -0.28) = 0.0
    assert score == 0.0

def test_behavior_history_aggregation():
    ba = BehaviorAnalysis()
    interactions = [
        {"reel_id": "R1", "watch_percentage": 0.95, "liked": 1, "saved": 1, "shared": 0, "rewatched": 1, "skipped": 0},
        {"reel_id": "R2", "watch_percentage": 0.10, "liked": 0, "saved": 0, "shared": 0, "rewatched": 0, "skipped": 1},
        {"reel_id": "R3", "watch_percentage": 0.80, "liked": 1, "saved": 0, "shared": 0, "rewatched": 0, "skipped": 0}
    ]
    summary = ba.analyze_interaction_history(interactions)
    assert summary["total_interactions"] == 3
    assert summary["like_rate"] == round(2/3, 4)
    assert summary["skip_rate"] == round(1/3, 4)
    assert len(summary["scored_interactions"]) == 3
