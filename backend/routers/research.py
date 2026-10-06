import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from database import get_supabase_client
from agents.discovery import DiscoveryAgent
from agents.research import ResearchAgent
from schemas.research import ResearchProcessResult

logger = logging.getLogger("techpulse.routers.research")
router = APIRouter(prefix="/api/research", tags=["Research & Verification"])


class ResearchRunResponse(BaseModel):
    candidate_stories_processed: int
    canonical_stories_created: int
    claims_extracted: int
    claims_confirmed: int
    claims_disputed: int
    claims_unconfirmed: int
    average_confidence: float
    results: List[ResearchProcessResult]
    failed_stories: List[Dict[str, str]]


@router.post("/run", response_model=ResearchRunResponse)
async def run_research_and_verification_pipeline(
    limit: int = Query(default=10, ge=1, le=50, description="Max candidate stories to investigate"),
    min_relevance: float = Query(default=0.50, ge=0.0, le=1.0, description="Minimum relevance score to qualify")
) -> Dict[str, Any]:
    """
    Executes the Research & Verification pipeline:
    1. Evaluates candidate stories from Discovery.
    2. Investigates factual claims and gathers evidence.
    3. Runs deterministic verification and confidence scoring.
    4. Persists canonical records in 'stories', 'story_sources', and 'claims'.
    5. Records full telemetry in 'agent_runs'.
    """
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=500, detail="Database client not configured.")

    start_time = time.time()
    started_at = datetime.now(timezone.utc).isoformat()

    # 1. Record start in agent_runs
    agent_run_id = None
    try:
        run_insert = supabase.table("agent_runs").insert({
            "agent_name": "ResearchVerificationAgent",
            "run_type": "MANUAL_TRIGGER",
            "status": "RUNNING",
            "started_at": started_at,
            "input_payload": {"limit": limit, "min_relevance": min_relevance},
            "output_payload": {},
            "tokens_used": 0,
            "duration_ms": 0
        }).execute()
        if run_insert.data:
            agent_run_id = run_insert.data[0]["id"]
    except Exception as e:
        logger.error(f"Failed to create agent_run record: {e}")

    try:
        # 2. Fetch submissions to form candidate story bundles
        # Prioritize unprocessed submissions, fallback to latest 100
        subs_res = supabase.table("submissions") \
            .select("*") \
            .eq("processed", False) \
            .order("published_at", desc=True) \
            .limit(150) \
            .execute()
        
        submissions_pool = subs_res.data or []
        if not submissions_pool:
            subs_res = supabase.table("submissions") \
                .select("*") \
                .order("published_at", desc=True) \
                .limit(100) \
                .execute()
            submissions_pool = subs_res.data or []

        if not submissions_pool:
            logger.warning("No submissions available to research.")
            return {
                "candidate_stories_processed": 0,
                "canonical_stories_created": 0,
                "claims_extracted": 0,
                "claims_confirmed": 0,
                "claims_disputed": 0,
                "claims_unconfirmed": 0,
                "average_confidence": 0.0,
                "results": [],
                "failed_stories": []
            }

        # 3. Form candidate stories using Discovery Agent
        discovery_agent = DiscoveryAgent(relevance_threshold=min_relevance)
        discovery_res = discovery_agent.run(submissions_pool)
        candidate_stories = discovery_res.get("candidate_stories", [])

        # Filter and slice to requested limit
        qualifying_candidates = [
            c for c in candidate_stories 
            if c.get("relevance_score", 0.0) >= min_relevance
        ][:limit]

        # 4. Process each candidate story with error isolation
        research_agent = ResearchAgent()
        processed_results: List[ResearchProcessResult] = []
        failed_stories: List[Dict[str, str]] = []

        for cand in qualifying_candidates:
            try:
                res = await research_agent.process_and_persist_story(cand, supabase)
                processed_results.append(res)
            except Exception as story_err:
                logger.error(f"Failed to process candidate story '{cand.get('title')}': {story_err}", exc_info=True)
                failed_stories.append({
                    "title": cand.get("title", "Unknown"),
                    "error": str(story_err)
                })

        # 5. Aggregate metrics
        total_created = len(processed_results)
        total_claims = sum(r.claims_count for r in processed_results)
        total_confirmed = sum(r.claims_confirmed for r in processed_results)
        total_disputed = sum(r.claims_disputed for r in processed_results)
        total_unconfirmed = sum(r.claims_unconfirmed for r in processed_results)
        avg_confidence = (
            round(sum(r.confidence for r in processed_results) / total_created, 1)
            if total_created > 0 else 0.0
        )

        duration_ms = int((time.time() - start_time) * 1000)
        completed_at = datetime.now(timezone.utc).isoformat()

        response_payload = {
            "candidate_stories_processed": len(qualifying_candidates),
            "canonical_stories_created": total_created,
            "claims_extracted": total_claims,
            "claims_confirmed": total_confirmed,
            "claims_disputed": total_disputed,
            "claims_unconfirmed": total_unconfirmed,
            "average_confidence": avg_confidence,
            "results": processed_results,
            "failed_stories": failed_stories
        }

        # 6. Record completion in agent_runs
        if agent_run_id:
            supabase.table("agent_runs").update({
                "status": "SUCCESS",
                "completed_at": completed_at,
                "duration_ms": duration_ms,
                "output_payload": {
                    "candidate_stories_processed": len(qualifying_candidates),
                    "canonical_stories_created": total_created,
                    "claims_extracted": total_claims,
                    "claims_confirmed": total_confirmed,
                    "claims_disputed": total_disputed,
                    "claims_unconfirmed": total_unconfirmed,
                    "average_confidence": avg_confidence,
                    "failed_count": len(failed_stories)
                }
            }).eq("id", agent_run_id).execute()

        return response_payload

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        completed_at = datetime.now(timezone.utc).isoformat()
        logger.error(f"Research pipeline fatal error: {e}", exc_info=True)

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

        raise HTTPException(status_code=500, detail=f"Research pipeline error: {str(e)}")
