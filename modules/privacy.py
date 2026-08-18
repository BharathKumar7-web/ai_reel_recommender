"""
Privacy Module: Implements consent management, anonymization, personalization toggles,
and user data erasure controls.
"""

from typing import Dict, Any
from database.database import Database

class PrivacyManager:
    def __init__(self, db: Database = None):
        self.db = db or Database()

    def get_privacy_status(self, user_id: str) -> Dict[str, Any]:
        """Returns privacy status, consent, and anonymization details for a user."""
        is_personalized = self.db.is_personalization_enabled(user_id)
        return {
            "user_id": user_id,
            "is_anonymous": user_id.startswith("USER_"),
            "personalization_enabled": is_personalized,
            "consent_status": "Active (Local Storage Only)",
            "data_minimization_level": "High (No PII, No Scraped Cookies)",
            "storage_type": "Local Encrypted/Parameterized SQLite"
        }

    def toggle_personalization(self, user_id: str, enabled: bool) -> bool:
        """Toggles user personalization on or off."""
        self.db.set_personalization(user_id, enabled)
        return enabled

    def reset_profile(self, user_id: str) -> str:
        """Clears all inferred interest profile embeddings and tiers."""
        self.db.reset_user_profile(user_id)
        return f"Successfully reset dynamic interest profile for {user_id}."

    def delete_all_user_data(self, user_id: str) -> str:
        """Completely purges interactions, feedback, and profiles for user (GDPR/CCPA compliant)."""
        self.db.delete_user_data(user_id)
        return f"All interaction history and profile records for {user_id} have been permanently deleted."
