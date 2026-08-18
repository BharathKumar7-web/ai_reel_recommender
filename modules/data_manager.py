"""
Data Manager Module: High-level data accessor and manager.
"""

import os
from typing import List, Dict, Any
from database.database import Database

class DataManager:
    def __init__(self, data_dir: str = None, db: Database = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        self.db = db or Database()
        self.db.seed_data(self.data_dir)

    def get_reels(self) -> List[Dict[str, Any]]:
        return self.db.get_all_reels()

    def get_recommendations(self) -> List[Dict[str, Any]]:
        return self.db.get_all_recommendations()

    def get_user_interactions(self, user_id: str) -> List[Dict[str, Any]]:
        return self.db.get_user_interactions(user_id)

    def record_interaction(self, user_id: str, reel_id: str, watch_percentage: float,
                           liked: bool = False, saved: bool = False, shared: bool = False,
                           rewatched: bool = False, skipped: bool = False, engagement_score: float = 0.0):
        self.db.record_interaction(user_id, reel_id, watch_percentage, liked, saved, shared, rewatched, skipped, engagement_score)

    def seed_hackathon_scenario(self, user_id: str = "USER_001"):
        self.db.seed_hackathon_trap_scenario(user_id)

    def get_user_profile(self, user_id: str) -> Dict[str, float]:
        return self.db.get_user_profile(user_id)

    def save_user_profile(self, user_id: str, profile: Dict[str, float]):
        self.db.save_interest_profile(user_id, profile)
