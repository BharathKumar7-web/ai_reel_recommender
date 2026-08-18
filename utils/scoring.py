"""
Mathematical scoring and weighting routines for behavior analysis and ranking.
"""

from typing import Dict, Any

# Configurable behavior engagement weights
DEFAULT_BEHAVIOR_WEIGHTS = {
    "watch_completion": 0.40,
    "like": 0.20,
    "save": 0.20,
    "share": 0.10,
    "rewatch": 0.10,
    "skip_penalty": 0.30
}

# Configurable ranking component weights
DEFAULT_RANKING_WEIGHTS = {
    "relevance": 0.25,
    "interest_match": 0.25,
    "educational_value": 0.20,
    "quality": 0.10,
    "difficulty_match": 0.10,
    "diversity": 0.05,
    "exploration": 0.05,
    "hype_penalty": 0.35
}

def calculate_engagement_score(
    watch_percentage: float,
    liked: bool = False,
    saved: bool = False,
    shared: bool = False,
    rewatched: bool = False,
    skipped: bool = False,
    weights: Dict[str, float] = None
) -> float:
    """
    Computes normalized user engagement score [0.0, 1.0] from interaction signals.
    Formula:
      Score = w_wc * watch_completion + w_lk * like + w_sv * save + w_sh * share + w_rw * rewatch - w_sk * skip
    """
    w = weights or DEFAULT_BEHAVIOR_WEIGHTS
    raw_score = (
        w["watch_completion"] * min(max(watch_percentage, 0.0), 1.0)
        + w["like"] * (1.0 if liked else 0.0)
        + w["save"] * (1.0 if saved else 0.0)
        + w["share"] * (1.0 if shared else 0.0)
        + w["rewatch"] * (1.0 if rewatched else 0.0)
        - (w["skip_penalty"] if skipped else 0.0)
    )
    return round(float(min(max(raw_score, 0.0), 1.0)), 4)

def calculate_difficulty_match_score(user_level: str, item_difficulty: str) -> float:
    """
    Computes alignment score between user proficiency and content difficulty.
    Levels: Beginner (1), Intermediate (2), Advanced (3).
    """
    levels = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
    u_idx = levels.get(user_level, 2)
    i_idx = levels.get(item_difficulty, 2)
    diff = abs(u_idx - i_idx)
    if diff == 0:
        return 1.0
    elif diff == 1:
        return 0.70
    else:
        return 0.30

def calculate_composite_rank_score(
    relevance: float,
    interest_match: float,
    educational_value: float,
    quality: float,
    difficulty_match: float,
    diversity_bonus: float,
    exploration_bonus: float,
    hype_penalty: float,
    weights: Dict[str, float] = None
) -> Dict[str, float]:
    """
    Computes composite multi-signal recommendation score with full component attribution.
    """
    w = weights or DEFAULT_RANKING_WEIGHTS
    pos_score = (
        w["relevance"] * relevance
        + w["interest_match"] * interest_match
        + w["educational_value"] * educational_value
        + w["quality"] * quality
        + w["difficulty_match"] * difficulty_match
        + w["diversity"] * diversity_bonus
        + w["exploration"] * exploration_bonus
    )
    penalty = w["hype_penalty"] * hype_penalty
    final_score = max(pos_score - penalty, 0.0)

    return {
        "final_score": round(final_score, 4),
        "relevance_contrib": round(w["relevance"] * relevance, 4),
        "interest_contrib": round(w["interest_match"] * interest_match, 4),
        "edu_contrib": round(w["educational_value"] * educational_value, 4),
        "quality_contrib": round(w["quality"] * quality, 4),
        "diff_contrib": round(w["difficulty_match"] * difficulty_match, 4),
        "diversity_contrib": round(w["diversity"] * diversity_bonus, 4),
        "exploration_contrib": round(w["exploration"] * exploration_bonus, 4),
        "hype_penalty_deduction": round(penalty, 4)
    }
