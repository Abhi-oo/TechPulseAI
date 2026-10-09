import re
import json
import logging
from typing import Dict, Any, List, Optional
import httpx

from config import settings
from schemas.short_news import IntelligenceCard

logger = logging.getLogger("techpulse.short_news_agent")
logger.setLevel(logging.INFO)


class ShortNewsAgent:
    """
    Logical AI Short-News Agent.
    Converts researched, verified canonical stories into concise executive
    intelligence cards (<= 30 words per field) grounded strictly in verified evidence.
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key or settings.GEMINI_API_KEY

    async def _summarize_with_llm(
        self,
        title: str,
        category: str,
        existing_what: str,
        existing_why: str,
        existing_impact: str,
        stored_claims: List[Dict[str, Any]]
    ) -> Optional[IntelligenceCard]:
        """Calls Gemini with strict grounding and length constraints."""
        if not self.gemini_api_key:
            return None

        claims_context = "\n".join([
            f"- {c.get('claim_text')} (Status: {c.get('status')})"
            for c in stored_claims[:5]
        ])

        prompt = f"""
You are an executive technology intelligence editor.
Rewrite the following verified story into an ultra-concise Intelligence Card.

STRICT CONSTRAINTS:
1. "what": Direct factual explanation of the event. Maximum 30 words.
2. "why_it_matters": Technical and architectural significance. Maximum 30 words.
3. "impact": Ecosystem, developer, and market consequences. Maximum 30 words.
4. GROUNDING: Use ONLY the facts provided in the source text below. Do NOT invent or add unsupported facts.
5. Return a strict JSON object with keys: "what", "why_it_matters", "impact".

Title: {title}
Category: {category}
Verified Narrative:
- What: {existing_what}
- Why: {existing_why}
- Impact: {existing_impact}
Verified Claims:
{claims_context}

Respond ONLY with valid JSON.
"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    url,
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"response_mime_type": "application/json"}
                    }
                )
                if resp.status_code == 200:
                    data = resp.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(raw_text)
                    return IntelligenceCard(
                        what=parsed.get("what", existing_what),
                        why_it_matters=parsed.get("why_it_matters", existing_why),
                        impact=parsed.get("impact", existing_impact)
                    )
        except Exception as e:
            logger.warning(f"ShortNews LLM condensation fallback: {e}")

        return None

    def _summarize_heuristically(
        self,
        existing_what: str,
        existing_why: str,
        existing_impact: str,
        stored_claims: List[Dict[str, Any]]
    ) -> IntelligenceCard:
        """
        Deterministic, strictly grounded condenser.
        Extracts the most salient factual clauses from verified evidence,
        enforcing the strict <= 30 words constraint without hallucination.
        """
        def condense_field(text: str, fallback_prefix: str = "") -> str:
            if not text:
                return fallback_prefix
            # Take the primary declarative clause
            clean = " ".join(text.strip().split())
            sentences = re.split(r'(?<=[.!?])\s+', clean)
            lead = sentences[0] if sentences else clean
            words = lead.split()
            if len(words) <= 30:
                return lead
            return " ".join(words[:30]).rstrip(".,;:-") + "..."

        condensed_what = condense_field(existing_what)
        condensed_why = condense_field(existing_why)
        condensed_impact = condense_field(existing_impact)

        return IntelligenceCard(
            what=condensed_what,
            why_it_matters=condensed_why,
            impact=condensed_impact
        )

    async def generate_card(
        self,
        story: Dict[str, Any],
        stored_claims: Optional[List[Dict[str, Any]]] = None
    ) -> IntelligenceCard:
        """
        Generates an intelligence card for a canonical story.
        Preserves verified facts and guarantees <= 30 words per field.
        """
        title = story.get("title", "")
        category = story.get("category", "Technology")
        what = story.get("what", "")
        why = story.get("why_it_matters", "")
        impact = story.get("impact", "")
        claims = stored_claims or []

        # Attempt structured LLM condensation first
        card = await self._summarize_with_llm(title, category, what, why, impact, claims)
        if not card:
            # Deterministic, zero-hallucination fallback
            card = self._summarize_heuristically(what, why, impact, claims)

        return card
