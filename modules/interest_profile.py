"""
Dynamic Interest Profile Module: Manages multi-interest profiles, tier classifications,
and temporal interest evolution.
"""

from typing import Dict, Any, List
from datetime import datetime

class InterestProfileManager:
    def __init__(self):
        pass

    def categorize_interests(self, profile: Dict[str, float]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorizes interest dimensions into Primary, Secondary, Emerging, and Weak tiers.
        """
        categorized = {
            "Primary": [],
            "Secondary": [],
            "Emerging": [],
            "Weak": []
        }
        for name, score in sorted(profile.items(), key=lambda x: x[1], reverse=True):
            entry = {"name": name, "score": round(score, 2)}
            if score >= 0.75:
                categorized["Primary"].append(entry)
            elif score >= 0.50:
                categorized["Secondary"].append(entry)
            elif score >= 0.30:
                categorized["Emerging"].append(entry)
            else:
                categorized["Weak"].append(entry)
        return categorized

    def simulate_temporal_evolution(self, current_profile: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Generates simulated multi-week temporal evolution trend data for visualization.
        Demonstrates how interests shifted over time (e.g. Week 1 -> Week 2 -> Week 3).
        """
        swe_score = current_profile.get("Software Engineering", 0.88)
        ai_score = current_profile.get("AI", 0.72)
        dsa_score = current_profile.get("DSA", 0.61)
        java_score = current_profile.get("Java", 0.55)

        return [
            {
                "time_period": "Week 1 (Onboarding)",
                "Software Engineering": round(swe_score * 0.65, 2),
                "Java": round(java_score * 1.25, 2),
                "AI": round(ai_score * 0.30, 2),
                "DSA": round(dsa_score * 0.40, 2)
            },
            {
                "time_period": "Week 2 (Exploring)",
                "Software Engineering": round(swe_score * 0.85, 2),
                "Java": round(java_score * 1.10, 2),
                "AI": round(ai_score * 0.65, 2),
                "DSA": round(dsa_score * 0.75, 2)
            },
            {
                "time_period": "Week 3 (Current State)",
                "Software Engineering": round(swe_score, 2),
                "Java": round(java_score, 2),
                "AI": round(ai_score, 2),
                "DSA": round(dsa_score, 2)
            }
        ]

    def blend_feedback_into_profile(
        self,
        current_profile: Dict[str, float],
        target_category: str,
        delta: float
    ) -> Dict[str, float]:
        """
        Updates profile scores dynamically upon receiving feedback signals.
        """
        updated = current_profile.copy()
        current_val = updated.get(target_category, 0.40)
        new_val = max(min(current_val + delta, 0.98), 0.05)
        updated[target_category] = round(new_val, 2)
        return updated
