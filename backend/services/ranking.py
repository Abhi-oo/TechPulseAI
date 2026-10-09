import math
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from schemas.short_news import RankingComponents

logger = logging.getLogger("techpulse.ranking")
logger.setLevel(logging.INFO)

# Strategic ecosystem impact weights by technology category
CATEGORY_IMPACT_WEIGHTS = {
    "LLMs & GenAI": 85.0,
    "Hardware & Silicon": 85.0,
    "Robotics & Autonomous": 80.0,
    "OpenSource & Frameworks": 75.0,
    "AI Safety & Security": 75.0,
    "Cloud & Infrastructure": 70.0,
    "Technology": 60.0
}


def calculate_ranking_components(
    story: Dict[str, Any],
    stored_claims: Optional[List[Dict[str, Any]]] = None,
    now_dt: Optional[datetime] = None
) -> RankingComponents:
    """
    Calculates a deterministic ranking score (0.0 to 100.0) based on:
    - Recency (30%)
    - Importance (30%)
    - Impact (20%)
    - Confidence (20%)
    
    Each component is strictly normalized to a 0.0 - 100.0 scale before combining.
    Handles missing values safely.
    """
    current_time = now_dt or datetime.now(timezone.utc)

    # 1. Recency Normalization (30% weight)
    ts_str = story.get("last_updated_at") or story.get("first_seen_at") or story.get("created_at")
    age_hours = 0.0
    if ts_str:
        try:
            # Handle ISO string with potential timezone offsets
            clean_ts = ts_str.replace("Z", "+00:00")
            parsed_dt = datetime.fromisoformat(clean_ts)
            if parsed_dt.tzinfo is None:
                parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
            delta = current_time - parsed_dt
            age_hours = max(0.0, delta.total_seconds() / 3600.0)
        except Exception as e:
            logger.debug(f"Timestamp parse fallback for {ts_str}: {e}")
            age_hours = 0.0

    # Exponential decay over 48 hours: 0h -> 100, 24h -> ~60.6, 48h -> ~36.8, floored at 5.0
    recency_norm = max(5.0, min(100.0, 100.0 * math.exp(-age_hours / 48.0)))

    # 2. Importance Normalization (30% weight)
    # Stored importance_score is on a 1.0 - 10.0 scale in the schema
    raw_importance = story.get("importance_score")
    if raw_importance is None or not isinstance(raw_importance, (int, float)):
        raw_importance = 5.0
    importance_norm = max(0.0, min(100.0, float(raw_importance) * 10.0))

    # 3. Impact Normalization (20% weight)
    category = story.get("category", "Technology")
    base_impact = CATEGORY_IMPACT_WEIGHTS.get(category, 60.0)
    claims_count = len(stored_claims or [])
    # Claims corroboration depth bonus (+5 per claim, max +15)
    claim_bonus = min(15.0, claims_count * 5.0)
    impact_norm = max(0.0, min(100.0, base_impact + claim_bonus))

    # 4. Confidence Normalization (20% weight)
    # Confidence is stored as 0 - 100 in the schema
    raw_confidence = story.get("confidence")
    if raw_confidence is None or not isinstance(raw_confidence, (int, float)):
        raw_confidence = 50.0
    confidence_norm = max(0.0, min(100.0, float(raw_confidence)))

    # Combined Ranking Score: 30% + 30% + 20% + 20% = 100%
    final_score = round(
        (0.30 * recency_norm) +
        (0.30 * importance_norm) +
        (0.20 * impact_norm) +
        (0.20 * confidence_norm),
        2
    )

    explanation = (
        f"Recency: {recency_norm:.1f}/100 (age: {age_hours:.1f}h) [30%] | "
        f"Importance: {importance_norm:.1f}/100 [30%] | "
        f"Impact: {impact_norm:.1f}/100 [20%] | "
        f"Confidence: {confidence_norm:.1f}/100 [20%] -> "
        f"Rank: {final_score:.2f}/100"
    )

    return RankingComponents(
        recency_norm=round(recency_norm, 2),
        importance_norm=round(importance_norm, 2),
        impact_norm=round(impact_norm, 2),
        confidence_norm=round(confidence_norm, 2),
        ranking_score=final_score,
        age_hours=round(age_hours, 2),
        explanation=explanation
    )


def determine_verified_status(
    confidence: int,
    stored_claims: Optional[List[Dict[str, Any]]] = None,
    desired_status: str = "VERIFIED"
) -> str:
    """
    CRITICAL SAFETY GUARD:
    Prevents low-confidence or disputed stories from appearing as definitively verified.
    Keeps ranking separate from confidence: a high-ranking breaking story with low
    confidence remains flagged as UNVERIFIED / DRAFT until factual corroboration is attained.
    """
    claims = stored_claims or []
    has_disputed = any(c.get("status") == "DISPUTED" for c in claims)

    # If confidence < 50 or claims are actively disputed, block 'VERIFIED'
    if confidence < 50 or has_disputed:
        return "DRAFT"

    return desired_status
