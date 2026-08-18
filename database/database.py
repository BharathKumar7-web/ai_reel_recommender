"""
Database Manager for AI Reel Recommender
Implements SQLite schema, parameterized queries, and privacy operations.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recommender.db")

class Database:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initializes tables using safe parameterized DDL."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    persona TEXT,
                    personalization_enabled INTEGER DEFAULT 1,
                    created_at TEXT
                )
            """)

            # Reels catalog table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reels (
                    reel_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    caption TEXT,
                    transcript TEXT,
                    description TEXT,
                    category TEXT,
                    topic TEXT,
                    difficulty TEXT,
                    content_type TEXT,
                    quality_score REAL,
                    video_url TEXT,
                    tags TEXT
                )
            """)

            # Migration: Ensure video_url exists if table was created previously
            cursor.execute("PRAGMA table_info(reels)")
            cols = [r["name"] for r in cursor.fetchall()]
            if "video_url" not in cols and len(cols) > 0:
                cursor.execute("ALTER TABLE reels ADD COLUMN video_url TEXT")

            # Interactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    reel_id TEXT,
                    watch_percentage REAL,
                    liked INTEGER DEFAULT 0,
                    saved INTEGER DEFAULT 0,
                    shared INTEGER DEFAULT 0,
                    rewatched INTEGER DEFAULT 0,
                    skipped INTEGER DEFAULT 0,
                    engagement_score REAL DEFAULT 0.0,
                    timestamp TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (reel_id) REFERENCES reels(reel_id)
                )
            """)

            # Interest profiles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interest_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    interest_name TEXT,
                    score REAL,
                    interest_tier TEXT,
                    updated_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            # Recommendations catalog
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    rec_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    topic TEXT,
                    difficulty TEXT,
                    educational_value REAL,
                    quality_score REAL,
                    credibility_score REAL,
                    hype_score REAL,
                    content_type TEXT,
                    tags TEXT
                )
            """)

            # Recommendation history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recommendation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    rec_id TEXT,
                    score REAL,
                    reason TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            # Feedback table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    rec_id TEXT,
                    feedback_type TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            # Privacy settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS privacy_settings (
                    user_id TEXT PRIMARY KEY,
                    consent_given INTEGER DEFAULT 1,
                    data_retention_days INTEGER DEFAULT 30,
                    personalization_enabled INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)

            conn.commit()

    def seed_data(self, data_dir: str):
        """Seeds base datasets from JSON files if tables are empty."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Seed Users
            users_file = os.path.join(data_dir, "users.json")
            if os.path.exists(users_file):
                cursor.execute("SELECT COUNT(*) as count FROM users")
                if cursor.fetchone()["count"] == 0:
                    with open(users_file, "r", encoding="utf-8") as f:
                        users = json.load(f)
                        for u in users:
                            cursor.execute(
                                "INSERT OR IGNORE INTO users (user_id, persona, personalization_enabled, created_at) VALUES (?, ?, ?, ?)",
                                (u["user_id"], u["persona"], int(u.get("personalization_enabled", True)), u.get("created_at", datetime.now().isoformat()))
                            )
                            cursor.execute(
                                "INSERT OR IGNORE INTO privacy_settings (user_id, consent_given, personalization_enabled) VALUES (?, 1, ?)",
                                (u["user_id"], int(u.get("personalization_enabled", True)))
                            )

            # Seed Reels
            reels_file = os.path.join(data_dir, "reels.json")
            if os.path.exists(reels_file):
                with open(reels_file, "r", encoding="utf-8") as f:
                    reels = json.load(f)
                    for r in reels:
                        cursor.execute("""
                            INSERT OR REPLACE INTO reels 
                            (reel_id, title, caption, transcript, description, category, topic, difficulty, content_type, quality_score, video_url, tags)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            r["reel_id"], r["title"], r.get("caption", ""), r.get("transcript", ""),
                            r.get("description", ""), r.get("category", "Other"), r.get("topic", ""),
                            r.get("difficulty", "Beginner"), r.get("content_type", ""),
                            float(r.get("quality_score", 0.8)), r.get("video_url", ""), json.dumps(r.get("tags", []))
                        ))

            # Seed Recommendations
            recs_file = os.path.join(data_dir, "recommendations.json")
            if os.path.exists(recs_file):
                cursor.execute("SELECT COUNT(*) as count FROM recommendations")
                if cursor.fetchone()["count"] == 0:
                    with open(recs_file, "r", encoding="utf-8") as f:
                        recs = json.load(f)
                        for rec in recs:
                            cursor.execute("""
                                INSERT OR REPLACE INTO recommendations
                                (rec_id, title, description, category, topic, difficulty, educational_value, quality_score, credibility_score, hype_score, content_type, tags)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                rec["rec_id"], rec["title"], rec.get("description", ""), rec.get("category", "Other"),
                                rec.get("topic", ""), rec.get("difficulty", "Intermediate"),
                                float(rec.get("educational_value", 0.9)), float(rec.get("quality_score", 0.9)),
                                float(rec.get("credibility_score", 0.9)), float(rec.get("hype_score", 0.1)),
                                rec.get("content_type", ""), json.dumps(rec.get("tags", []))
                            ))

            conn.commit()

    # --- Interaction Operations ---
    def record_interaction(self, user_id: str, reel_id: str, watch_percentage: float,
                           liked: bool = False, saved: bool = False, shared: bool = False,
                           rewatched: bool = False, skipped: bool = False, engagement_score: float = 0.0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO interactions
                (user_id, reel_id, watch_percentage, liked, saved, shared, rewatched, skipped, engagement_score, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, reel_id, watch_percentage, int(liked), int(saved),
                int(shared), int(rewatched), int(skipped), engagement_score,
                datetime.utcnow().isoformat()
            ))
            conn.commit()

    def get_user_interactions(self, user_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT i.*, r.title, r.category, r.topic, r.content_type, r.tags, r.difficulty
                FROM interactions i
                LEFT JOIN reels r ON i.reel_id = r.reel_id
                WHERE i.user_id = ?
                ORDER BY i.id ASC
            """, (user_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_all_reels(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reels")
            rows = cursor.fetchall()
            res = []
            for r in rows:
                item = dict(r)
                item["tags"] = json.loads(item["tags"]) if item.get("tags") else []
                res.append(item)
            return res

    def get_all_recommendations(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recommendations")
            rows = cursor.fetchall()
            res = []
            for r in rows:
                item = dict(r)
                item["tags"] = json.loads(item["tags"]) if item.get("tags") else []
                res.append(item)
            return res

    # --- Interest Profile Operations ---
    def save_interest_profile(self, user_id: str, profile_dict: Dict[str, float]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM interest_profiles WHERE user_id = ?", (user_id,))
            now = datetime.utcnow().isoformat()
            for interest, score in profile_dict.items():
                tier = "Primary" if score >= 0.75 else "Secondary" if score >= 0.50 else "Emerging" if score >= 0.30 else "Weak"
                cursor.execute("""
                    INSERT INTO interest_profiles (user_id, interest_name, score, interest_tier, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, interest, score, tier, now))
            conn.commit()

    def get_user_profile(self, user_id: str) -> Dict[str, float]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT interest_name, score FROM interest_profiles WHERE user_id = ? ORDER BY score DESC", (user_id,))
            rows = cursor.fetchall()
            return {row["interest_name"]: float(row["score"]) for row in rows}

    # --- Feedback Operations ---
    def record_feedback(self, user_id: str, rec_id: str, feedback_type: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback (user_id, rec_id, feedback_type, timestamp)
                VALUES (?, ?, ?, ?)
            """, (user_id, rec_id, feedback_type, datetime.utcnow().isoformat()))
            conn.commit()

    def get_user_feedback(self, user_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM feedback WHERE user_id = ? ORDER BY id DESC", (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    # --- Privacy Controls ---
    def set_personalization(self, user_id: str, enabled: bool):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_id, persona, personalization_enabled, created_at)
                VALUES (?, 'Anonymous User', ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET personalization_enabled = excluded.personalization_enabled
            """, (user_id, int(enabled), datetime.utcnow().isoformat()))
            cursor.execute("""
                INSERT INTO privacy_settings (user_id, consent_given, personalization_enabled)
                VALUES (?, 1, ?)
                ON CONFLICT(user_id) DO UPDATE SET personalization_enabled = excluded.personalization_enabled
            """, (user_id, int(enabled)))
            conn.commit()

    def is_personalization_enabled(self, user_id: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT personalization_enabled FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row is not None:
                return bool(row["personalization_enabled"])
            cursor.execute("SELECT personalization_enabled FROM privacy_settings WHERE user_id = ?", (user_id,))
            row_priv = cursor.fetchone()
            return bool(row_priv["personalization_enabled"]) if row_priv is not None else True

    def reset_user_profile(self, user_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM interest_profiles WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM recommendation_history WHERE user_id = ?", (user_id,))
            conn.commit()

    def delete_user_data(self, user_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM interactions WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM interest_profiles WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM recommendation_history WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM feedback WHERE user_id = ?", (user_id,))
            conn.commit()

    def seed_hackathon_trap_scenario(self, user_id: str = "USER_001"):
        """
        Seeds the exact hackathon demo scenario:
        Student watches:
        1. REEL_001: Java meme (95% watch, Liked, Rewatched)
        2. REEL_002: SWE lifestyle (100% watch, Saved)
        3. REEL_003: Coding interview joke (90% watch, Liked)
        4. REEL_004: Laptop comparison for devs (85% watch, Saved)
        5. REEL_005: AI dev APIs (88% watch, Liked, Shared)
        6. REEL_006: DSA Binary search overflow (100% watch, Saved)
        """
        self.delete_user_data(user_id)
        interactions = [
            ("REEL_001", 0.95, True, False, False, True, False, 0.92),
            ("REEL_002", 1.00, True, True, False, False, False, 0.98),
            ("REEL_003", 0.90, True, False, False, False, False, 0.88),
            ("REEL_004", 0.85, False, True, False, False, False, 0.84),
            ("REEL_005", 0.88, True, False, True, False, False, 0.90),
            ("REEL_006", 1.00, True, True, False, False, False, 0.99),
        ]
        for reel_id, wp, lk, sv, sh, rw, sk, eng in interactions:
            self.record_interaction(
                user_id=user_id,
                reel_id=reel_id,
                watch_percentage=wp,
                liked=lk,
                saved=sv,
                shared=sh,
                rewatched=rw,
                skipped=sk,
                engagement_score=eng
            )
