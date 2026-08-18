"""
Ranking Engine Module: Multi-signal scoring and ranking for candidate recommendations.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from utils.scoring import calculate_composite_rank_score, calculate_difficulty_match_score, DEFAULT_RANKING_WEIGHTS
from utils.embeddings import EmbeddingEngine
from modules.quality_filter import QualityFilter
from modules.diversity_engine import DiversityEngine
from modules.exploration_engine import ExplorationEngine

class RankingEngine:
    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        embedding_engine: Optional[EmbeddingEngine] = None,
        quality_filter: Optional[QualityFilter] = None,
        diversity_engine: Optional[DiversityEngine] = None,
        exploration_engine: Optional[ExplorationEngine] = None
    ):
        self.weights = weights or DEFAULT_RANKING_WEIGHTS.copy()
        self.embedder = embedding_engine or EmbeddingEngine()
        self.quality_filter = quality_filter or QualityFilter()
        self.diversity_engine = diversity_engine or DiversityEngine()
        self.exploration_engine = exploration_engine or ExplorationEngine()

    def rank_candidates(
        self,
        candidates: List[Dict[str, Any]],
        user_profile: Dict[str, float],
        current_reel: Optional[Dict[str, Any]],
        interaction_history: List[Dict[str, Any]],
        user_difficulty_tier: str = "Intermediate",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Ranks candidate recommendations using normalized multi-signal weighting.
        """
        if not candidates:
            return []

        # Current Reel vector
        current_vec = None
        if current_reel:
            current_text = f"{current_reel.get('title', '')} {current_reel.get('description', '')} {current_reel.get('category', '')}"
            current_vec = self.embedder.get_embedding(current_text)

        recent_categories = [i.get("category", "") for i in interaction_history[-5:] if i.get("category")]
        primary_interests = [k for k, v in user_profile.items() if v >= 0.70]
        emerging_interests = [k for k, v in user_profile.items() if 0.30 <= v < 0.60]

        scored_candidates = []
        selected_categories: List[str] = []

        for item in candidates:
            category = item.get("category", "Other")
            item_text = f"{item.get('title', '')} {item.get('description', '')} {item.get('topic', '')}"
            item_vec = self.embedder.get_embedding(item_text)

            # 1. Semantic Relevance
            relevance = self.embedder.compute_similarity(current_vec, item_vec) if current_vec is not None else 0.70

            # 2. Interest Match from User Profile
            # Direct or parent domain match
            interest_match = user_profile.get(category, 0.0)
            if "Software Engineering" in user_profile and category in ["AI", "DSA", "Java", "HLD", "Cloud", "Hardware", "Cybersecurity"]:
                interest_match = max(interest_match, user_profile["Software Engineering"] * 0.90)

            # 3. Quality & Anti-Hype Evaluation
            quality_eval = self.quality_filter.evaluate_content_quality(item)
            edu_val = quality_eval["educational_value"]
            quality = quality_eval["quality_score"]
            hype_penalty = quality_eval["penalty_magnitude"]

            # 4. Difficulty Match
            diff_match = calculate_difficulty_match_score(user_difficulty_tier, item.get("difficulty", "Intermediate"))

            # 5. Diversity & Exploration
            diversity_bonus = self.diversity_engine.calculate_diversity_bonus(category, recent_categories, selected_categories)
            exploration_bonus = self.exploration_engine.calculate_exploration_bonus(category, primary_interests, emerging_interests)

            # 6. Composite Score
            score_decomp = calculate_composite_rank_score(
                relevance=relevance,
                interest_match=interest_match,
                educational_value=edu_val,
                quality=quality,
                difficulty_match=diff_match,
                diversity_bonus=diversity_bonus,
                exploration_bonus=exploration_bonus,
                hype_penalty=hype_penalty,
                weights=self.weights
            )

            res = item.copy()
            res.update({
                "final_score": score_decomp["final_score"],
                "relevance": round(relevance, 3),
                "interest_match": round(interest_match, 3),
                "educational_value": round(edu_val, 3),
                "quality_score": round(quality, 3),
                "difficulty_match": round(diff_match, 3),
                "diversity_bonus": round(diversity_bonus, 3),
                "exploration_bonus": round(exploration_bonus, 3),
                "hype_penalty": round(hype_penalty, 3),
                "score_breakdown": score_decomp,
                "quality_evaluation": quality_eval
            })
            scored_candidates.append(res)
            selected_categories.append(category)

        # Sort descending by final score
        scored_candidates.sort(key=lambda x: x["final_score"], reverse=True)
        return scored_candidates[:top_k]
