"""
Recommendation Engine Module: Coordinates candidate generation, cold-start handling,
and difficulty tier estimation.
"""

from typing import List, Dict, Any, Optional
from modules.ranking_engine import RankingEngine
from modules.interest_inference import InterestInferenceEngine
from database.database import Database

class RecommendationEngine:
    def __init__(
        self,
        ranking_engine: Optional[RankingEngine] = None,
        inference_engine: Optional[InterestInferenceEngine] = None,
        db: Optional[Database] = None
    ):
        self.ranking_engine = ranking_engine or RankingEngine()
        self.inference_engine = inference_engine or InterestInferenceEngine()
        self.db = db or Database()

    def estimate_user_difficulty(self, interactions: List[Dict[str, Any]]) -> str:
        """
        Estimates user proficiency tier based on the difficulty distribution of completed reels.
        """
        if not interactions:
            return "Intermediate"

        diff_scores = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
        total_weight = 0.0
        weighted_sum = 0.0

        for i in interactions:
            diff = i.get("difficulty", "Intermediate")
            val = diff_scores.get(diff, 2)
            eng = float(i.get("engagement_score", 0.5))
            weighted_sum += val * eng
            total_weight += eng

        if total_weight == 0:
            return "Intermediate"

        avg = weighted_sum / total_weight
        if avg < 1.6:
            return "Beginner"
        elif avg <= 2.4:
            return "Intermediate"
        else:
            return "Advanced"

    def get_recommendations(
        self,
        user_id: str,
        current_reel_id: Optional[str] = None,
        top_k: int = 3
    ) -> Dict[str, Any]:
        """
        Generates top-k recommendations for a user, handling cold start and active profiles.
        """
        # 1. Fetch data
        interactions = self.db.get_user_interactions(user_id)
        reels_catalog = self.db.get_all_reels()
        candidates = self.db.get_all_recommendations()

        # Find current reel
        current_reel = next((r for r in reels_catalog if r["reel_id"] == current_reel_id), None)
        if not current_reel and interactions:
            last_reel_id = interactions[-1]["reel_id"]
            current_reel = next((r for r in reels_catalog if r["reel_id"] == last_reel_id), None)

        # 2. Check personalization status
        is_personalized = self.db.is_personalization_enabled(user_id)

        # 3. Infer interests
        if is_personalized:
            inference_res = self.inference_engine.infer_interests(interactions, reels_catalog)
            user_profile = inference_res["interest_scores"]
            self.db.save_interest_profile(user_id, user_profile)
        else:
            inference_res = {
                "interest_scores": {},
                "primary_interests": ["General Technology"],
                "secondary_interests": [],
                "emerging_interests": [],
                "weak_interests": [],
                "underlying_interest": "General Technology (Personalization Disabled)",
                "evidence": ["Personalization disabled by user privacy settings."],
                "confidence": "Low",
                "confidence_score": 0.0,
                "is_cold_start": True
            }
            user_profile = {}

        # 4. Determine user difficulty
        user_difficulty = self.estimate_user_difficulty(interactions)

        # 5. Rank candidates
        ranked_recs = self.ranking_engine.rank_candidates(
            candidates=candidates,
            user_profile=user_profile,
            current_reel=current_reel,
            interaction_history=interactions,
            user_difficulty_tier=user_difficulty,
            top_k=top_k
        )

        return {
            "user_id": user_id,
            "current_reel": current_reel,
            "inference": inference_res,
            "user_difficulty": user_difficulty,
            "recommendations": ranked_recs,
            "personalization_enabled": is_personalized
        }
