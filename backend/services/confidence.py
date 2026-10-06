import logging
from typing import List, Dict, Any
from schemas.research import ConfidenceBreakdown, VerifiedClaimResult

logger = logging.getLogger("techpulse.confidence")
logger.setLevel(logging.INFO)


def calculate_story_confidence(
    sources_meta: List[Dict[str, Any]],
    claims: List[VerifiedClaimResult]
) -> ConfidenceBreakdown:
    """
    Computes a deterministic, explainable confidence score (0 to 100) based on:
    1. Source reliability weights
    2. Primary source presence
    3. Independent domain corroboration
    4. Source claim agreement vs dispute
    5. Evidence coverage depth
    """
    # 1. Source Reliability (max 25 pts)
    weights = [s.get("reliability_weight", 1.0) for s in sources_meta]
    avg_weight = sum(weights) / max(1, len(weights))
    if avg_weight >= 1.3:
        reliability_score = 25.0
    elif avg_weight >= 1.1:
        reliability_score = 20.0
    else:
        reliability_score = 15.0

    # 2. Primary Source Bonus (max 20 pts)
    has_primary = any(s.get("tier") == "PRIMARY" for s in sources_meta)
    has_verified = any(s.get("tier") == "VERIFIED_NEWS" for s in sources_meta)
    if has_primary:
        primary_bonus = 20.0
    elif has_verified:
        primary_bonus = 12.0
    else:
        primary_bonus = 6.0

    # 3. Independent Corroboration (max 25 pts)
    domains = {s.get("domain") for s in sources_meta if s.get("domain")}
    num_domains = len(domains)
    if num_domains >= 3:
        corroboration_score = 25.0
    elif num_domains == 2:
        corroboration_score = 18.0
    else:
        corroboration_score = 10.0

    # 4. Source Agreement vs Dispute (max 20 pts)
    total_claims = len(claims)
    if total_claims == 0:
        agreement_score = 10.0
    else:
        confirmed_count = sum(1 for c in claims if c.status == "CONFIRMED")
        disputed_count = sum(1 for c in claims if c.status == "DISPUTED")
        unconfirmed_count = sum(1 for c in claims if c.status == "UNCONFIRMED")

        # Heavily penalize disputes, reward consensus
        net_agreement = (confirmed_count * 1.0 + unconfirmed_count * 0.4 - disputed_count * 1.5) / total_claims
        agreement_ratio = max(0.0, min(1.0, net_agreement))
        agreement_score = round(agreement_ratio * 20.0, 1)

    # 5. Evidence Depth (max 10 pts)
    if total_claims == 0:
        evidence_depth_score = 5.0
    else:
        total_evidence_items = sum(len(c.evidence) for c in claims)
        avg_evidence = total_evidence_items / total_claims
        if avg_evidence >= 2.0:
            evidence_depth_score = 10.0
        elif avg_evidence >= 1.0:
            evidence_depth_score = 7.0
        else:
            evidence_depth_score = 3.0

    raw_total = reliability_score + primary_bonus + corroboration_score + agreement_score + evidence_depth_score
    # Strictly bound between 20 and 95 (no single RSS story is 100% infallible or 0%)
    final_confidence = int(max(20, min(95, round(raw_total))))

    explanation = (
        f"Reliability: {reliability_score}/25 (avg weight {avg_weight:.2f}) | "
        f"Primary Tier: {primary_bonus}/20 | "
        f"Corroboration: {corroboration_score}/25 ({num_domains} domains) | "
        f"Agreement: {agreement_score}/20 | "
        f"Evidence Depth: {evidence_depth_score}/10"
    )

    return ConfidenceBreakdown(
        source_reliability_score=reliability_score,
        primary_source_bonus=primary_bonus,
        corroboration_score=corroboration_score,
        agreement_score=agreement_score,
        evidence_depth_score=evidence_depth_score,
        total_confidence=final_confidence,
        explanation=explanation
    )
