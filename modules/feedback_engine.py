"""
Feedback Engine Module: Collects implicit and explicit feedback and executes closed-loop profile updates.
"""

from typing import Dict, Any, Optional
from database.database import Database
from modules.interest_profile import InterestProfileManager

class FeedbackEngine:
    def __init__(self, db: Optional[Database] = None, profile_manager: Optional[InterestProfileManager] = None):
        self.db = db or Database()
        self.profile_manager = profile_manager or InterestProfileManager()

    def process_feedback(
        self,
        user_id: str,
        rec_id: str,
        feedback_type: str,
        rec_category: str
    ) -> Dict[str, Any]:
        """
        Records feedback and applies positive/negative delta to the user's interest profile.
        """
        # 1. Record in DB
        self.db.record_feedback(user_id, rec_id, feedback_type)

        # 2. Determine feedback weight
        # Positive adjustments
        feedback_deltas = {
            "like": +0.06,
            "save": +0.08,
            "useful": +0.10,
            "relevant_career": +0.12,
            "show_more": +0.10,
            "rewatch": +0.05,
            # Negative adjustments
            "skip": -0.05,
            "not_relevant": -0.12,
            "too_difficult": -0.04,
            "too_basic": -0.04,
            "clickbait": -0.15,
            "dislike": -0.10
        }

        delta = feedback_deltas.get(feedback_type, 0.0)

        # 3. Update active profile
        current_profile = self.db.get_user_profile(user_id)
        if current_profile and rec_category:
            updated_profile = self.profile_manager.blend_feedback_into_profile(
                current_profile, rec_category, delta
            )
            self.db.save_interest_profile(user_id, updated_profile)
            new_score = updated_profile.get(rec_category, 0.5)
        else:
            new_score = 0.5

        return {
            "user_id": user_id,
            "rec_id": rec_id,
            "feedback_type": feedback_type,
            "category": rec_category,
            "delta_applied": delta,
            "updated_category_score": new_score,
            "message": f"Recorded '{feedback_type}' feedback. Adjusted {rec_category} score by {delta:+.2f}."
        }
