import re
import logging
from typing import List, Dict, Any
from schemas.research import ExtractedClaim, ClaimEvidence, VerifiedClaimResult

logger = logging.getLogger("techpulse.verification")
logger.setLevel(logging.INFO)

CONTRADICTION_CUES = [
    r"\bdenies\b", r"\bdenied\b", r"\brefutes\b", r"\brefuted\b",
    r"\bdebunked?\b", r"\bcontrary to\b", r"\bdisputed?\b",
    r"\bnot true\b", r"\bfalse\b", r"\bfails to replicate\b",
    r"\bunproven\b", r"\bmisleading\b", r"\bwalks? back\b",
    r"\bincorrect\b", r"\bno evidence\b"
]


def _detect_stance(claim_keywords: List[str], text_snippet: str) -> str:
    """Detects whether text supports or contradicts a claim."""
    snippet_lower = text_snippet.lower()

    # Check for contradiction cues
    for pattern in CONTRADICTION_CUES:
        if re.search(pattern, snippet_lower):
            return "CONTRADICTS"

    # Count matching claim keywords in the snippet
    matched = sum(1 for kw in claim_keywords if re.search(r'\b' + re.escape(kw) + r'\b', snippet_lower))
    if matched >= max(1, len(claim_keywords) // 2):
        return "SUPPORTS"

    return "NEUTRAL"


def verify_claim(claim: ExtractedClaim, articles: List[Dict[str, Any]]) -> VerifiedClaimResult:
    """
    Evaluates a single claim across all available articles in the bundle.
    Detects supporting, contradicting, and neutral evidence, and classifies
    the claim as CONFIRMED, DISPUTED, or UNCONFIRMED.
    """
    # Extract significant keywords (length > 3)
    words = re.findall(r'\b[a-zA-Z0-9_\-]{3,}\b', claim.claim_text.lower())
    stop_words = {"this", "that", "with", "from", "have", "more", "also", "been", "were", "which", "about"}
    keywords = [w for w in words if w not in stop_words][:8]

    collected_evidence: List[ClaimEvidence] = []
    supporting_domains = set()
    contradicting_domains = set()

    for art in articles:
        content = art.get("cleaned_content") or art.get("raw_content") or ""
        title = art.get("title") or ""
        full_text = f"{title}. {content}"

        source_name = art.get("source_name") or art.get("author") or "Unknown Source"
        source_url = art.get("url") or ""

        # Break text into sentences to extract local evidence quotes
        sentences = re.split(r'(?<=[.!?])\s+', full_text)
        best_quote = ""
        best_stance = "NEUTRAL"

        for sent in sentences:
            sent_clean = sent.strip()
            if len(sent_clean) < 15:
                continue

            stance = _detect_stance(keywords, sent_clean)
            if stance in ("SUPPORTS", "CONTRADICTS"):
                best_quote = sent_clean[:280]
                best_stance = stance
                break

        if not best_quote and len(sentences) > 0:
            # Fallback to first non-empty snippet if any keywords match
            for sent in sentences:
                if any(kw in sent.lower() for kw in keywords):
                    best_quote = sent.strip()[:280]
                    best_stance = "SUPPORTS"
                    break

        if best_quote:
            evidence_item = ClaimEvidence(
                source_name=source_name,
                source_url=source_url,
                quote=best_quote,
                stance=best_stance
            )
            collected_evidence.append(evidence_item)

            domain = art.get("domain") or source_name
            if best_stance == "SUPPORTS":
                supporting_domains.add(domain)
            elif best_stance == "CONTRADICTS":
                contradicting_domains.add(domain)

    # Classification rules:
    # 1. DISPUTED: At least 1 supporting and 1 contradicting source
    if len(contradicting_domains) >= 1 and len(supporting_domains) >= 1:
        status = "DISPUTED"
    # 2. CONFIRMED: At least 2 distinct independent sources supporting with 0 contradictions
    elif len(supporting_domains) >= 2 and len(contradicting_domains) == 0:
        status = "CONFIRMED"
    # 3. UNCONFIRMED: Only 1 source supports (or unsupported)
    else:
        status = "UNCONFIRMED"

    corroboration_count = max(1, len(supporting_domains))

    return VerifiedClaimResult(
        claim_text=claim.claim_text,
        status=status,
        corroboration_count=corroboration_count,
        evidence=collected_evidence
    )


def verify_all_claims(claims: List[ExtractedClaim], articles: List[Dict[str, Any]]) -> List[VerifiedClaimResult]:
    """Verifies a list of claims against a set of articles."""
    return [verify_claim(c, articles) for c in claims]
