"""
Anomaly Detection Module: Detects isolated outlier interactions to prevent profile corruption.
"""

from typing import List, Dict, Any, Tuple
import numpy as np

class AnomalyDetector:
    def __init__(self, outlier_threshold: float = 0.35):
        self.outlier_threshold = outlier_threshold

    def filter_anomalous_interactions(
        self,
        interactions: List[Dict[str, Any]],
        reel_embeddings_map: Dict[str, np.ndarray]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Detects interactions that are distant from the user's historical centroid
        and damps their influence.
        """
        if len(interactions) < 4:
            # Not enough data to reliably declare an anomaly
            return interactions, []

        # 1. Compute user semantic centroid across all previous high-engagement interactions
        vectors = []
        for inter in interactions:
            reel_id = inter.get("reel_id")
            if reel_id in reel_embeddings_map:
                vectors.append(reel_embeddings_map[reel_id])

        if not vectors:
            return interactions, []

        centroid = np.mean(vectors, axis=0)
        norm = np.linalg.norm(centroid)
        if norm > 0:
            centroid = centroid / norm

        sanitized_interactions = []
        anomalies_detected = []

        for inter in interactions:
            reel_id = inter.get("reel_id")
            emb = reel_embeddings_map.get(reel_id)
            eng = float(inter.get("engagement_score", inter.get("calculated_engagement", 0.8)))

            if emb is not None:
                sim_to_centroid = float(np.dot(centroid, emb) / (np.linalg.norm(emb) + 1e-7))
                # If interaction is very distant from historical centroid despite high engagement
                if sim_to_centroid < self.outlier_threshold and eng > 0.70:
                    damped_item = inter.copy()
                    damped_eng = eng * 0.40  # Damp outlier influence by 60%
                    damped_item["engagement_score"] = damped_eng
                    damped_item["is_anomaly"] = True
                    damped_item["anomaly_reason"] = f"Isolated high engagement in unrelated domain (similarity {sim_to_centroid:.2f})"
                    sanitized_interactions.append(damped_item)
                    anomalies_detected.append(damped_item)
                    continue

            sanitized_interactions.append(inter)

        return sanitized_interactions, anomalies_detected
