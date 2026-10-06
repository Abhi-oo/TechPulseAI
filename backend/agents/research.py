import re
import json
import logging
from uuid import uuid4
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional

import httpx

from config import settings
from schemas.research import (
    ExtractedClaim,
    StoryNarrative,
    VerifiedClaimResult,
    ResearchProcessResult,
    ConfidenceBreakdown
)
from services.verification import verify_all_claims
from services.confidence import calculate_story_confidence

logger = logging.getLogger("techpulse.research_agent")
logger.setLevel(logging.INFO)


def _slugify(text: str) -> str:
    """Generates a clean URL slug from title."""
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', text.lower())
    slug = re.sub(r'[\s_-]+', '-', clean).strip('-')
    return slug[:280] or "tech-story"


class ResearchAgent:
    """
    Logical AI Research & Verification Agent.
    1. Extracts factual claims and synthesizes technical narrative (What, Why it matters, Impact).
    2. Gathers and compares evidence across linked sources.
    3. Runs deterministic verification and confidence scoring.
    4. Persists canonical story, story_sources, and claims in Supabase.
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key or settings.GEMINI_API_KEY

    async def _extract_with_llm(
        self,
        candidate_title: str,
        category: str,
        combined_text: str
    ) -> Optional[Tuple[StoryNarrative, List[ExtractedClaim]]]:
        """Attempts structured narrative and claim extraction using Gemini API."""
        if not self.gemini_api_key:
            return None

        prompt = f"""
You are an expert technology intelligence analyst.
Analyze the following technology news bundle and return a strict JSON object with:
1. "title": Clear, concise canonical headline (max 200 chars).
2. "category": Chosen from ["LLMs & GenAI", "Hardware & Silicon", "Robotics & Autonomous", "OpenSource & Frameworks", "AI Safety & Security", "Cloud & Infrastructure"].
3. "what": Direct factual explanation of what happened (2-3 sentences).
4. "why_it_matters": Technical and architectural depth (2-3 sentences explaining engineering significance).
5. "impact": Ecosystem, developer, or industry implications (2-3 sentences).
6. "claims": A list of 2 to 4 concrete, verifiable factual claims. Each claim must have:
   - "claim_text": The specific statement of fact (e.g. "Model achieves 92.4% on MMLU benchmark").
   - "claim_type": "BENCHMARK", "ARCHITECTURE", "RELEASE", or "METRIC".
   - "needed_evidence": What evidence proves or disproves this claim.

Content to analyze:
Title: {candidate_title}
Category: {category}
Text: {combined_text[:4000]}

Respond ONLY with valid JSON.
"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                resp = await client.post(
                    url,
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"response_mime_type": "application/json"}
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(raw_json)

                    narrative = StoryNarrative(
                        title=parsed.get("title", candidate_title),
                        category=parsed.get("category", category),
                        what=parsed.get("what", ""),
                        why_it_matters=parsed.get("why_it_matters", ""),
                        impact=parsed.get("impact", "")
                    )
                    claims = [
                        ExtractedClaim(
                            claim_text=c.get("claim_text", ""),
                            claim_type=c.get("claim_type", "FACT"),
                            needed_evidence=c.get("needed_evidence", "")
                        )
                        for c in parsed.get("claims", [])
                        if c.get("claim_text")
                    ]
                    if claims and narrative.what:
                        return narrative, claims
        except Exception as e:
            logger.warning(f"LLM extraction fallback triggered: {e}")

        return None

    def _extract_heuristically(
        self,
        candidate_title: str,
        category: str,
        articles: List[Dict[str, Any]]
    ) -> Tuple[StoryNarrative, List[ExtractedClaim]]:
        """
        Deterministic, high-precision extractor for claim extraction and technical narrative.
        Ensures 100% reliability even when LLM API keys are absent or rate-limited.
        """
        full_text = " ".join([
            (a.get("cleaned_content") or a.get("title") or "")
            for a in articles
        ])
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', full_text) if len(s.strip()) > 25]

        # Extract factual claim candidates containing action verbs or metrics
        claim_patterns = [
            r"\b(achieves?|outperforms?|exceeds?|improves?|reduces?)\b",
            r"\b(releases?|announces?|unveils?|publishes?|open-sources?)\b",
            r"\b(\d+(\.\d+)?%|\d+x|\d+\s*(gb|tb|parameters|flops|tokens))\b",
            r"\b(benchmark|latency|throughput|accuracy|score)\b"
        ]

        extracted_claims: List[ExtractedClaim] = []
        seen_claims = set()

        for sent in sentences:
            if any(re.search(pat, sent, re.IGNORECASE) for pat in claim_patterns):
                clean_sent = " ".join(sent.split())
                if clean_sent not in seen_claims and len(clean_sent) < 220:
                    seen_claims.add(clean_sent)
                    claim_type = "BENCHMARK" if "%" in clean_sent or "score" in clean_sent.lower() else "RELEASE"
                    extracted_claims.append(ExtractedClaim(
                        claim_text=clean_sent,
                        claim_type=claim_type,
                        needed_evidence=f"Corroborating technical documentation or benchmark report for '{clean_sent[:60]}'"
                    ))
            if len(extracted_claims) >= 3:
                break

        # Fallback if no specific regex matched
        if not extracted_claims:
            lead_claim = candidate_title
            extracted_claims.append(ExtractedClaim(
                claim_text=lead_claim,
                claim_type="ANNOUNCEMENT",
                needed_evidence="Independent announcement or verification from official technical source."
            ))

        # Narrative Triad Synthesis
        what_text = sentences[0] if sentences else candidate_title
        why_text = (
            sentences[1] if len(sentences) > 1
            else f"This represents a significant architectural progression in {category}, impacting efficiency and deployment standards."
        )
        impact_text = (
            sentences[2] if len(sentences) > 2
            else f"Broadens developer access and accelerates industry capability across the {category} landscape."
        )

        narrative = StoryNarrative(
            title=candidate_title,
            category=category,
            what=what_text,
            why_it_matters=why_text,
            impact=impact_text
        )

        return narrative, extracted_claims

    async def investigate_candidate(
        self,
        candidate: Dict[str, Any],
        articles: List[Dict[str, Any]],
        sources_meta: List[Dict[str, Any]]
    ) -> Tuple[StoryNarrative, List[VerifiedClaimResult], ConfidenceBreakdown]:
        """
        Runs claim extraction, evidence investigation, verification, and confidence calculation.
        """
        title = candidate.get("title", "Untitled Story")
        category = candidate.get("category", "Technology")

        combined_text = " ".join([
            f"{a.get('title')}: {a.get('cleaned_content', '')}"
            for a in articles
        ])

        # 1. Extract narrative and claims (LLM with deterministic fallback)
        extraction = await self._extract_with_llm(title, category, combined_text)
        if not extraction:
            narrative, claims = self._extract_heuristically(title, category, articles)
        else:
            narrative, claims = extraction

        # 2. Verify all claims across available articles
        verified_claims = verify_all_claims(claims, articles)

        # 3. Calculate deterministic confidence
        confidence_breakdown = calculate_story_confidence(sources_meta, verified_claims)

        return narrative, verified_claims, confidence_breakdown

    async def process_and_persist_story(
        self,
        candidate: Dict[str, Any],
        supabase_client
    ) -> ResearchProcessResult:
        """
        Researches candidate story and persists canonical Story, StorySources, and Claims in Supabase.
        """
        sub_ids = candidate.get("submission_ids", [])
        if not sub_ids:
            raise ValueError(f"Candidate story '{candidate.get('title')}' has no submission_ids.")

        # Fetch full submission records
        subs_res = supabase_client.table("submissions").select("*").in_("id", sub_ids).execute()
        articles = subs_res.data or []
        if not articles:
            raise ValueError(f"Submissions not found in DB for ids: {sub_ids}")

        # Fetch associated source records
        source_ids = list({a["source_id"] for a in articles if a.get("source_id")})
        sources_meta = []
        if source_ids:
            src_res = supabase_client.table("sources").select("*").in_("id", source_ids).execute()
            sources_meta = src_res.data or []

        # Map source info into articles for citation and evidence tracing
        source_by_id = {s["id"]: s for s in sources_meta}
        for art in articles:
            s_info = source_by_id.get(art.get("source_id"))
            if s_info:
                art["source_name"] = s_info.get("name")
                art["domain"] = s_info.get("domain")

        # Prioritize primary sources in investigation
        articles.sort(key=lambda a: 1 if source_by_id.get(a.get("source_id"), {}).get("tier") == "PRIMARY" else 0, reverse=True)

        # Run investigation
        narrative, verified_claims, confidence_breakdown = await self.investigate_candidate(
            candidate, articles, sources_meta
        )

        now_iso = datetime.now(timezone.utc).isoformat()
        slug_base = _slugify(narrative.title)
        slug = f"{slug_base}-{uuid4().hex[:6]}"

        # 1. Insert or update canonical story in stories table
        story_payload = {
            "title": narrative.title[:300],
            "slug": slug,
            "category": narrative.category[:50],
            "what": narrative.what,
            "why_it_matters": narrative.why_it_matters,
            "impact": narrative.impact,
            "confidence": confidence_breakdown.total_confidence,
            "importance_score": 7.0 if confidence_breakdown.total_confidence >= 70 else 5.0,
            "ranking_score": round(confidence_breakdown.total_confidence / 10.0, 2),
            "status": "VERIFIED",
            "first_seen_at": articles[0].get("published_at", now_iso),
            "last_updated_at": now_iso,
            "update_count": 0
        }

        story_insert = supabase_client.table("stories").insert(story_payload).execute()
        if not story_insert.data:
            raise RuntimeError(f"Failed to insert canonical story for '{narrative.title}'")

        story_record = story_insert.data[0]
        story_id = story_record["id"]

        # 2. Connect researched sources via story_sources
        story_source_records = []
        seen_urls = set()
        for idx, art in enumerate(articles):
            url = art.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                story_source_records.append({
                    "story_id": story_id,
                    "source_id": art["source_id"],
                    "submission_id": art["id"],
                    "article_url": url,
                    "article_title": (art.get("title") or "Article")[:300],
                    "is_primary_origin": (idx == 0)
                })

        if story_source_records:
            supabase_client.table("story_sources").insert(story_source_records).execute()

        # 3. Store claim evidence in claims table
        claims_records = []
        for vc in verified_claims:
            claims_records.append({
                "story_id": story_id,
                "claim_text": vc.claim_text,
                "status": vc.status,
                "corroboration_count": vc.corroboration_count,
                "evidence": [ev.model_dump() for ev in vc.evidence]
            })

        if claims_records:
            supabase_client.table("claims").insert(claims_records).execute()

        # Mark processed submissions
        supabase_client.table("submissions").update({"processed": True}).in_("id", sub_ids).execute()

        confirmed_count = sum(1 for c in verified_claims if c.status == "CONFIRMED")
        disputed_count = sum(1 for c in verified_claims if c.status == "DISPUTED")
        unconfirmed_count = sum(1 for c in verified_claims if c.status == "UNCONFIRMED")

        return ResearchProcessResult(
            story_id=story_id,
            title=narrative.title,
            category=narrative.category,
            confidence=confidence_breakdown.total_confidence,
            claims_count=len(verified_claims),
            claims_confirmed=confirmed_count,
            claims_disputed=disputed_count,
            claims_unconfirmed=unconfirmed_count,
            sources_linked=len(story_source_records),
            status="VERIFIED"
        )
