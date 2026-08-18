"""
Diversity Engine Module: Prevents echo-chamber repetition and promotes intra-list category variety.
"""

from typing import List, Dict, Any

class DiversityEngine:
    def __init__(self, repetition_penalty: float = 0.25):
        self.repetition_penalty = repetition_penalty

    def calculate_diversity_bonus(
        self,
        candidate_category: str,
        recent_history: List[str],
        current_top_candidates: List[str]
    ) -> float:
        """
        Computes a diversity bonus [0.0, 1.0] for a candidate.
        Penalizes categories that have appeared repeatedly in recent views or top candidate slots.
        """
        recent_count = recent_history.count(candidate_category)
        top_count = current_top_candidates.count(candidate_category)

        total_occurrences = recent_count + top_count
        if total_occurrences == 0:
            return 1.0  # Maximum novelty
        elif total_occurrences == 1:
            return 0.70
        elif total_occurrences == 2:
            return 0.40
        else:
            return max(1.0 - (total_occurrences * self.repetition_penalty), 0.10)

    def calculate_intra_list_diversity(self, recommendations: List[Dict[str, Any]]) -> float:
        """
        Measures the diversity ratio of unique categories across a list of recommendations.
        """
        if not recommendations:
            return 1.0
        categories = [r.get("category", "") for r in recommendations]
        unique_categories = set(categories)
        return round(len(unique_categories) / len(categories), 2)
