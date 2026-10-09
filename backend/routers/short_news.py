import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from database import get_supabase_client
from agents.short_news import ShortNewsAgent
from services.ranking import calculate_ranking_components, determine_verified_status
from schemas.short_news import ProcessedStorySummary

logger = logging.getLogger("techpulse.routers.short_news")
router = APIRouter(prefix="/api/short-news", tags=["Short-News & Ranking"])


class ShortNewsRunResponse(BaseModel):
    stories_processed: int
    stories_updated: int
    average_ranking_score: float
    results: List[ProcessedStorySummary]
    failed_stories: List[Dict[str, str]]


@router.post("/run", response_model=ShortNewsRunResponse)
async def run_short_news_and_ranking_pipeline(
    limit: int = Query(default=20, ge=1, le=100, description="Max stories to process and rank")
) -> Dict[str, Any]:
    """
    Executes the Short-News Generation & Ranking pipeline:
    1. Fetches canonical stories from Supabase.
    2. Synthesizes concise, evidence-grounded Intelligence Cards (<= 30 words per field).
    3. Calculates deterministic ranking scores (Recency 30%, Importance 30%, Impact 20%, Confidence 20%).
    4. Enforces safety verification guardrails for low-confidence or disputed stories.
    5. Updates existing canonical story records in-place in Supabase.
    6. Logs audit telemetry into 'agent_runs'.
    """
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=500, detail="Database client not configured.")

    start_time = time.time()
    started_at = datetime.now(timezone.utc).isoformat()

    # 1. Initialize audit record in agent_runs
    agent_run_id = None
    try:
        run_insert = supabase.table("agent_runs").insert({
            "agent_name": "ShortNewsAgent",
            "run_type": "MANUAL_TRIGGER",
            "status": "RUNNING",
            "started_at": started_at,
            "input_payload": {"limit": limit},
            "output_payload": {},
            "tokens_used": 0,
            "duration_ms": 0
        }).execute()
        if run_insert.data:
            agent_run_id = run_insert.data[0]["id"]
    except Exception as e:
        logger.error(f"Failed to create agent_run record: {e}")

    try:
        # 2. Query existing canonical stories
        stories_res = supabase.table("stories") \
            .select("*") \
            .order("last_updated_at", desc=True) \
            .limit(limit) \
            .execute()

        stories = stories_res.data or []
        if not stories:
            logger.info("No canonical stories found in database to process.")
            return {
                "stories_processed": 0,
                "stories_updated": 0,
                "average_ranking_score": 0.0,
                "results": [],
                "failed_stories": []
            }

        short_news_agent = ShortNewsAgent()
        processed_results: List[ProcessedStorySummary] = []
        failed_stories: List[Dict[str, str]] = []

        now_iso = datetime.now(timezone.utc).isoformat()

        # 3. Process each story with error isolation
        for story in stories:
            story_id = story["id"]
            try:
                # Fetch stored claims for this story
                claims_res = supabase.table("claims").select("*").eq("story_id", story_id).execute()
                stored_claims = claims_res.data or []

                # A. Generate concise intelligence card (<= 30 words per field)
                card = await short_news_agent.generate_card(story, stored_claims)

                # B. Calculate deterministic ranking score
                ranking = calculate_ranking_components(story, stored_claims)

                # C. Check verification guardrails
                safe_status = determine_verified_status(
                    confidence=story.get("confidence", 50),
                    stored_claims=stored_claims,
                    desired_status=story.get("status", "VERIFIED")
                )

                # D. Update existing story in Supabase (NO duplicates created)
                update_payload = {
                    "what": card.what,
                    "why_it_matters": card.why_it_matters,
                    "impact": card.impact,
                    "ranking_score": ranking.ranking_score,
                    "status": safe_status,
                    "last_updated_at": now_iso
                }

                supabase.table("stories").update(update_payload).eq("id", story_id).execute()

                processed_results.append(ProcessedStorySummary(
                    story_id=story_id,
                    title=story.get("title", ""),
                    category=story.get("category", "Technology"),
                    what=card.what,
                    why_it_matters=card.why_it_matters,
                    impact=card.impact,
                    confidence=story.get("confidence", 50),
                    ranking_score=ranking.ranking_score,
                    status=safe_status
                ))

            except Exception as story_err:
                logger.error(f"Failed to process story '{story.get('title')}': {story_err}", exc_info=True)
                failed_stories.append({
                    "story_id": story_id,
                    "title": story.get("title", "Unknown"),
                    "error": str(story_err)
                })

        # 4. Aggregate metrics
        total_updated = len(processed_results)
        avg_rank = (
            round(sum(r.ranking_score for r in processed_results) / total_updated, 2)
            if total_updated > 0 else 0.0
        )

        duration_ms = int((time.time() - start_time) * 1000)
        completed_at = datetime.now(timezone.utc).isoformat()

        response_payload = {
            "stories_processed": len(stories),
            "stories_updated": total_updated,
            "average_ranking_score": avg_rank,
            "results": processed_results,
            "failed_stories": failed_stories
        }

        # 5. Record telemetry in agent_runs
        if agent_run_id:
            supabase.table("agent_runs").update({
                "status": "SUCCESS",
                "completed_at": completed_at,
                "duration_ms": duration_ms,
                "output_payload": {
                    "stories_processed": len(stories),
                    "stories_updated": total_updated,
                    "average_ranking_score": avg_rank,
                    "failed_count": len(failed_stories)
                }
            }).eq("id", agent_run_id).execute()

        return response_payload

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        completed_at = datetime.now(timezone.utc).isoformat()
        logger.error(f"ShortNews pipeline fatal error: {e}", exc_info=True)

        if agent_run_id:
            try:
                supabase.table("agent_runs").update({
                    "status": "FAILED",
                    "completed_at": completed_at,
                    "duration_ms": duration_ms,
                    "error_message": str(e)
                }).eq("id", agent_run_id).execute()
            except Exception as log_err:
                logger.error(f"Failed to record failure in agent_runs: {log_err}")

        raise HTTPException(status_code=500, detail=f"ShortNews pipeline error: {str(e)}")
