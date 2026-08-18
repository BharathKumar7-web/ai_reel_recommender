"""
Behavior Analysis Module: Analyzes interaction signals, computes engagement scores, and aggregates behavioral metrics.
"""

from typing import List, Dict, Any, Optional
from utils.scoring import calculate_engagement_score, DEFAULT_BEHAVIOR_WEIGHTS

class BehaviorAnalysis:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or DEFAULT_BEHAVIOR_WEIGHTS.copy()

    def update_weights(self, new_weights: Dict[str, float]):
        self.weights.update(new_weights)

    def evaluate_interaction(self, interaction: Dict[str, Any]) -> float:
        """
        Calculates normalized engagement score for a single interaction.
        """
        return calculate_engagement_score(
            watch_percentage=float(interaction.get("watch_percentage", 0.0)),
            liked=bool(interaction.get("liked", 0)),
            saved=bool(interaction.get("saved", 0)),
            shared=bool(interaction.get("shared", 0)),
            rewatched=bool(interaction.get("rewatched", 0)),
            skipped=bool(interaction.get("skipped", 0)),
            weights=self.weights
        )

    def analyze_interaction_history(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregates behavioral metrics across multiple Reel interactions.
        """
        if not interactions:
            return {
                "total_interactions": 0,
                "avg_watch_percentage": 0.0,
                "avg_engagement_score": 0.0,
                "like_rate": 0.0,
                "save_rate": 0.0,
                "share_rate": 0.0,
                "rewatch_rate": 0.0,
                "skip_rate": 0.0,
                "high_engagement_reels": []
            }

        total = len(interactions)
        total_watch = sum(float(i.get("watch_percentage", 0.0)) for i in interactions)
        total_likes = sum(1 for i in interactions if i.get("liked"))
        total_saves = sum(1 for i in interactions if i.get("saved"))
        total_shares = sum(1 for i in interactions if i.get("shared"))
        total_rewatches = sum(1 for i in interactions if i.get("rewatched"))
        total_skips = sum(1 for i in interactions if i.get("skipped"))

        scored_interactions = []
        for i in interactions:
            score = self.evaluate_interaction(i)
            item = i.copy()
            item["calculated_engagement"] = score
            scored_interactions.append(item)

        avg_engagement = sum(i["calculated_engagement"] for i in scored_interactions) / total

        high_engagement_reels = [
            i for i in scored_interactions if i["calculated_engagement"] >= 0.70
        ]

        return {
            "total_interactions": total,
            "avg_watch_percentage": round(total_watch / total, 4),
            "avg_engagement_score": round(avg_engagement, 4),
            "like_rate": round(total_likes / total, 4),
            "save_rate": round(total_saves / total, 4),
            "share_rate": round(total_shares / total, 4),
            "rewatch_rate": round(total_rewatches / total, 4),
            "skip_rate": round(total_skips / total, 4),
            "high_engagement_reels": high_engagement_reels,
            "scored_interactions": scored_interactions
        }
