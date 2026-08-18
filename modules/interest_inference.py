"""
Interest Inference Module: Multi-Reel semantic reasoning engine.
Infers underlying interests, distinguishes surface keywords from deep intent,
and provides evidence and confidence scoring.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from modules.content_understanding import ContentUnderstanding
from modules.behavior_analysis import BehaviorAnalysis
from modules.anomaly_detection import AnomalyDetector
from utils.embeddings import EmbeddingEngine

# Semantic domain taxonomy for high-level interest clustering
DOMAIN_GRAPH = {
    "Software Engineering": ["Java", "Career", "DSA", "Cloud", "HLD", "Cybersecurity", "Programming", "Hardware"],
    "Artificial Intelligence": ["AI", "Machine Learning", "LLM", "Data Science"],
    "Algorithms & Systems": ["DSA", "HLD", "Cloud", "Hardware", "Cybersecurity"],
    "Career & Professional Development": ["Career", "Software Engineering", "DSA"],
    "Technology Hardware & Infrastructure": ["Hardware", "Cloud", "Workstation"],
    "Gaming & Entertainment": ["Gaming", "Entertainment"]
}

class InterestInferenceEngine:
    def __init__(
        self,
        content_engine: ContentUnderstanding = None,
        behavior_engine: BehaviorAnalysis = None,
        anomaly_detector: AnomalyDetector = None,
        embedding_engine: EmbeddingEngine = None
    ):
        self.embedder = embedding_engine or EmbeddingEngine()
        self.content_engine = content_engine or ContentUnderstanding(self.embedder)
        self.behavior_engine = behavior_engine or BehaviorAnalysis()
        self.anomaly_detector = anomaly_detector or AnomalyDetector()

    def infer_interests(
        self,
        interactions: List[Dict[str, Any]],
        reels_catalog: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Performs multi-Reel semantic reasoning over a sequence of user interactions.
        Returns dynamic interest scores, primary/secondary/emerging categories,
        evidence breakdown, and confidence evaluation.
        """
        if not interactions:
            return {
                "interest_scores": {},
                "primary_interests": [],
                "secondary_interests": [],
                "emerging_interests": [],
                "evidence": ["No interaction history available (Cold Start)."],
                "confidence": "Low",
                "confidence_score": 0.10,
                "underlying_interest": "General Technology",
                "is_cold_start": True
            }

        # 1. Map reels by ID and extract content features
        reels_map = {r["reel_id"]: r for r in reels_catalog}
        reel_embeddings = {}
        analyzed_reels = {}

        for reel in reels_catalog:
            analysis = self.content_engine.analyze_reel(reel)
            analyzed_reels[reel["reel_id"]] = analysis
            reel_embeddings[reel["reel_id"]] = analysis["embedding"]

        # 2. Score behavior engagement and filter anomalous one-off spikes
        history_stats = self.behavior_engine.analyze_interaction_history(interactions)
        scored_interactions = history_stats["scored_interactions"]
        sanitized_interactions, anomalies = self.anomaly_detector.filter_anomalous_interactions(
            scored_interactions, reel_embeddings
        )

        # 3. Multi-Reel Semantic & Behavioral Aggregation
        # Domain accumulation counters
        domain_weights: Dict[str, float] = {
            "Software Engineering": 0.0,
            "Programming": 0.0,
            "AI": 0.0,
            "DSA": 0.0,
            "Career": 0.0,
            "Hardware": 0.0,
            "Cloud": 0.0,
            "Cybersecurity": 0.0,
            "HLD": 0.0,
            "Gaming": 0.0
        }
        
        evidence_logs: List[str] = []
        interaction_count = len(sanitized_interactions)
        total_eng_mass = 0.0

        for inter in sanitized_interactions:
            reel_id = inter.get("reel_id")
            reel = reels_map.get(reel_id)
            if not reel:
                continue

            analysis = analyzed_reels.get(reel_id, {})
            category = reel.get("category", "Other")
            topic = reel.get("topic", category)
            eng = float(inter.get("engagement_score", inter.get("calculated_engagement", 0.5)))
            total_eng_mass += eng

            # Cross-topic semantic inference (e.g. Java + Coding Meme + SWE Lifestyle -> Software Engineering)
            if category in ["Java", "Career", "DSA", "Hardware", "Cloud"]:
                domain_weights["Software Engineering"] += eng * 0.95
                domain_weights["Programming"] += eng * 0.85
            if category == "Java":
                domain_weights["Java"] = domain_weights.get("Java", 0.0) + eng * 0.70
            if category == "AI":
                domain_weights["AI"] += eng * 1.10
                domain_weights["Software Engineering"] += eng * 0.40
            if category == "DSA":
                domain_weights["DSA"] += eng * 1.05
            if category == "Career":
                domain_weights["Career"] += eng * 0.90
            if category == "Hardware":
                domain_weights["Hardware"] += eng * 0.85
            if category == "Cloud":
                domain_weights["Cloud"] += eng * 1.00
                domain_weights["HLD"] += eng * 0.60
            if category == "Gaming":
                domain_weights["Gaming"] += eng * 0.90

            # Evidence generation
            action_desc = []
            if inter.get("watch_percentage", 0) >= 0.8:
                action_desc.append(f"{int(inter['watch_percentage']*100)}% watch completion")
            if inter.get("liked"):
                action_desc.append("liked")
            if inter.get("saved"):
                action_desc.append("saved")
            if inter.get("rewatched"):
                action_desc.append("rewatched")

            actions_str = ", ".join(action_desc) if action_desc else "viewed"
            evidence_logs.append(f"High engagement ({actions_str}) with '{reel['title']}' [{category} / {topic}]")

        # 4. Normalize scores to [0.0, 1.0]
        max_possible = max(total_eng_mass * 1.1, 1.0)
        normalized_scores = {}
        for domain, score in domain_weights.items():
            norm_val = round(min(score / max_possible, 0.98), 2)
            if norm_val > 0.05:
                normalized_scores[domain] = norm_val

        # Sort descending
        sorted_interests = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
        interest_dict = dict(sorted_interests)

        # 5. Tier Classification
        primary = [k for k, v in sorted_interests if v >= 0.75]
        secondary = [k for k, v in sorted_interests if 0.50 <= v < 0.75]
        emerging = [k for k, v in sorted_interests if 0.30 <= v < 0.50]
        weak = [k for k, v in sorted_interests if v < 0.30]

        # Top inferred underlying interest
        underlying_interest = primary[0] if primary else (secondary[0] if secondary else "Software Engineering")

        # 6. Confidence Calculation
        # Low: 1-2 reels, Medium: 3-5 reels, High: 6+ reels with high semantic consistency
        if interaction_count <= 2:
            confidence = "Low"
            confidence_score = round(min(0.20 + 0.15 * interaction_count, 0.45), 2)
        elif interaction_count <= 5:
            confidence = "Medium"
            confidence_score = round(0.50 + 0.07 * interaction_count, 2)
        else:
            confidence = "High"
            confidence_score = round(min(0.80 + 0.03 * interaction_count, 0.98), 2)

        return {
            "interest_scores": interest_dict,
            "primary_interests": primary,
            "secondary_interests": secondary,
            "emerging_interests": emerging,
            "weak_interests": weak,
            "underlying_interest": underlying_interest,
            "evidence": evidence_logs,
            "confidence": confidence,
            "confidence_score": confidence_score,
            "anomalies_detected": anomalies,
            "is_cold_start": interaction_count <= 2,
            "interaction_count": interaction_count
        }
