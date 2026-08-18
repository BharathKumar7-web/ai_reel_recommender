"""
Quality & Anti-Hype Filter Module: Detects clickbait, sensational claims, and unrealistic promises.
Calculates hype penalties to ensure high educational value.
"""

import re
from typing import Dict, Any, Tuple

# Trigger patterns indicative of low-educational hype/clickbait
HYPE_TRIGGERS = [
    r"\b10x\s+rich\b",
    r"\bmake\s+\$?[0-9,]+\b",
    r"\bget\s+rich\b",
    r"\bpassive\s+income\b",
    r"\breplace\s+programmers\b",
    r"\bdead\s+in\s+202[0-9]\b",
    r"\bguaranteed\s+job\b",
    r"\bsecret\s+hack\b",
    r"\bpassive\s+millions\b",
    r"\bzero\s+coding\b",
    r"\binstant\s+money\b",
    r"\binsane\b",
    r"\bshocking\b"
]

class QualityFilter:
    def __init__(self, hype_weight: float = 0.85):
        self.hype_weight = hype_weight

    def evaluate_content_quality(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assesses educational value, credibility, sensational language, and calculates a hype penalty.
        """
        title = item.get("title", "")
        desc = item.get("description", "")
        combined_text = f"{title} {desc}".lower()

        # 1. Base scores from metadata
        edu_val = float(item.get("educational_value", 0.70))
        quality = float(item.get("quality_score", 0.75))
        credibility = float(item.get("credibility_score", 0.80))
        raw_hype = float(item.get("hype_score", 0.10))

        # 2. Textual pattern detection
        matched_triggers = []
        for pattern in HYPE_TRIGGERS:
            if re.search(pattern, combined_text):
                matched_triggers.append(pattern.replace(r"\b", "").replace(r"\s+", " "))

        # Check for excessive capitalization in title
        upper_chars = sum(1 for c in title if c.isupper())
        total_letters = sum(1 for c in title if c.isalpha())
        caps_ratio = (upper_chars / total_letters) if total_letters > 0 else 0.0
        if caps_ratio > 0.35:
            matched_triggers.append("Excessive Uppercase Clickbait Styling")

        # 3. Dynamic Hype Calculation
        calculated_hype = min(raw_hype + 0.15 * len(matched_triggers), 1.0)
        calculated_credibility = max(credibility - 0.20 * len(matched_triggers), 0.10)

        # 4. Filter determination
        is_penalized = calculated_hype > 0.40 or len(matched_triggers) > 0
        penalty_magnitude = calculated_hype * self.hype_weight

        return {
            "is_penalized": is_penalized,
            "hype_score": round(calculated_hype, 3),
            "credibility_score": round(calculated_credibility, 3),
            "educational_value": round(edu_val, 3),
            "quality_score": round(quality, 3),
            "penalty_magnitude": round(penalty_magnitude, 3),
            "matched_triggers": matched_triggers,
            "quality_verdict": "Flagged as Hype/Clickbait" if is_penalized else "Verified Educational Content"
        }
