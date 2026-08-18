"""
Exploration Engine Module: Implements configurable Exploration vs Exploitation logic.
"""

from typing import Dict, Any, List

ADJACENT_DOMAIN_MAP = {
    "Software Engineering": ["Cloud", "HLD", "AI", "Cybersecurity", "Hardware"],
    "Java": ["HLD", "Cloud", "DSA", "Cybersecurity"],
    "DSA": ["HLD", "Software Engineering", "AI"],
    "AI": ["Software Engineering", "Cloud", "Cybersecurity"],
    "Gaming": ["Hardware", "Computer Science & Engineering", "Software Engineering"]
}

class ExplorationEngine:
    def __init__(self, exploration_weight: float = 0.20):
        self.exploration_weight = exploration_weight

    def set_exploration_weight(self, weight: float):
        self.exploration_weight = max(min(weight, 1.0), 0.0)

    def calculate_exploration_bonus(
        self,
        candidate_category: str,
        primary_interests: List[str],
        emerging_interests: List[str]
    ) -> float:
        """
        Calculates exploration score. If candidate category is an adjacent or emerging
        domain connected to the user's core interest, award exploration points.
        """
        # If candidate is in emerging interests
        if candidate_category in emerging_interests:
            return 1.0 * self.exploration_weight

        # Check adjacent knowledge graph
        for pri in primary_interests:
            adjacents = ADJACENT_DOMAIN_MAP.get(pri, [])
            if candidate_category in adjacents:
                return 0.85 * self.exploration_weight

        return 0.20 * self.exploration_weight
