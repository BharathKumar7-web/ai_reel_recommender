"""
Unit tests for Recommendation, Ranking, Anti-Hype Filtering, and Diversity.
"""

import pytest
from modules.quality_filter import QualityFilter
from modules.ranking_engine import RankingEngine
from modules.diversity_engine import DiversityEngine
from modules.evaluation import RecommenderEvaluator

def test_anti_hype_filter_penalizes_clickbait():
    qf = QualityFilter()
    
    clickbait_item = {
        "title": "10 INSANE AI Tools That Will Replace Programmers and Make You $10,000/Month FAST! 😱💰",
        "description": "Software engineering is dead! Copy paste these prompts to earn passive millions.",
        "educational_value": 0.15,
        "quality_score": 0.20,
        "credibility_score": 0.18,
        "hype_score": 0.95
    }
    
    educational_item = {
        "title": "AI-Assisted Software Development: Modern Workflows & LLM Orchestration",
        "description": "How engineers use agentic coding loops and structured output APIs in production.",
        "educational_value": 0.95,
        "quality_score": 0.94,
        "credibility_score": 0.96,
        "hype_score": 0.10
    }

    eval_clickbait = qf.evaluate_content_quality(clickbait_item)
    eval_edu = qf.evaluate_content_quality(educational_item)

    assert eval_clickbait["is_penalized"] is True
    assert eval_clickbait["penalty_magnitude"] > 0.60
    assert eval_edu["is_penalized"] is False
    assert eval_edu["penalty_magnitude"] < 0.20

def test_ranking_engine_ranks_educational_above_clickbait():
    ranking = RankingEngine()
    candidates = [
        {
            "rec_id": "REC_HYPE",
            "title": "10 INSANE AI Tools That Will Replace Programmers FAST!",
            "description": "Make $10,000 passive income with zero coding.",
            "category": "AI",
            "topic": "Get Rich AI",
            "difficulty": "Beginner",
            "educational_value": 0.15,
            "quality_score": 0.20,
            "credibility_score": 0.20,
            "hype_score": 0.95
        },
        {
            "rec_id": "REC_HIGH_VAL",
            "title": "AI-Assisted Software Development: Next-Gen Dev Workflows",
            "description": "Agentic coding loops and production systems.",
            "category": "AI",
            "topic": "AI in Software Engineering",
            "difficulty": "Intermediate",
            "educational_value": 0.95,
            "quality_score": 0.94,
            "credibility_score": 0.96,
            "hype_score": 0.10
        }
    ]

    user_profile = {"Software Engineering": 0.88, "AI": 0.80}
    current_reel = {"title": "OpenAI new dev APIs", "description": "SWE tools", "category": "AI"}

    ranked = ranking.rank_candidates(candidates, user_profile, current_reel, [])
    
    assert len(ranked) == 2
    assert ranked[0]["rec_id"] == "REC_HIGH_VAL"
    assert ranked[0]["final_score"] > ranked[1]["final_score"]

def test_diversity_bonus_penalizes_repetition():
    diversity = DiversityEngine()
    history = ["Java", "Java", "Java"]
    bonus_java = diversity.calculate_diversity_bonus("Java", history, ["Java"])
    bonus_cloud = diversity.calculate_diversity_bonus("Cloud", history, [])

    assert bonus_cloud > bonus_java
