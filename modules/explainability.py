"""
Explainability Module: Formats and generates transparent, human-readable explanations
adhering to the exact required schema.
"""

from typing import Dict, Any, Optional

class ExplainableAI:
    def __init__(self):
        pass

    def generate_recommendation_card(
        self,
        current_reel: Optional[Dict[str, Any]],
        inference_result: Dict[str, Any],
        recommended_reel: Dict[str, Any],
        user_difficulty: str = "Intermediate"
    ) -> Dict[str, Any]:
        """
        Builds the structured explanation matching the problem statement's exact output schema.
        """
        # Current Reel reference
        if current_reel:
            current_ref = f"{current_reel.get('title', 'Unknown')} [{current_reel.get('category', 'Other')}]"
        else:
            current_ref = "Session Onboarding / Initial Feed"

        # Interest detected
        interest_detected = inference_result.get("underlying_interest", "Software Engineering")
        
        # Why evidence
        evidence_list = inference_result.get("evidence", [])
        if evidence_list:
            why_evidence = " | ".join(evidence_list[:3])
        else:
            why_evidence = "Initial session exploration behavior."

        # Recommended Tech Reel
        rec_title = recommended_reel.get("title", "Technical Recommendation")
        category = recommended_reel.get("category", "Other")
        difficulty = recommended_reel.get("difficulty", user_difficulty)
        confidence = inference_result.get("confidence", "Medium")

        # Why this recommendation
        why_rec = (
            f"The system detected a broad interest in '{interest_detected}'. "
            f"Rather than shallowly repeating recent surface keywords, this recommendation provides high educational value "
            f"({int(recommended_reel.get('educational_value', 0.9)*100)}% rating) in '{category}' to accelerate practical skills."
        )

        formatted_text = f"""CURRENT REEL: {current_ref}
INTEREST DETECTED: {interest_detected}
WHY: {why_evidence}
RECOMMENDED TECH REEL: {rec_title}
CATEGORY: {category}
WHY THIS RECOMMENDATION: {why_rec}
DIFFICULTY: {difficulty}
CONFIDENCE: {confidence}"""

        score_decomp = recommended_reel.get("score_breakdown", {})

        return {
            "formatted_text": formatted_text,
            "current_reel": current_ref,
            "interest_detected": interest_detected,
            "why_evidence": why_evidence,
            "recommended_tech_reel": rec_title,
            "category": category,
            "why_recommendation": why_rec,
            "difficulty": difficulty,
            "confidence": confidence,
            "relevance_score": recommended_reel.get("relevance", 0.85),
            "interest_match": recommended_reel.get("interest_match", 0.90),
            "quality_score": recommended_reel.get("quality_score", 0.94),
            "educational_value": recommended_reel.get("educational_value", 0.95),
            "hype_penalty": recommended_reel.get("hype_penalty", 0.0),
            "final_score": recommended_reel.get("final_score", 0.92),
            "score_breakdown": score_decomp
        }
