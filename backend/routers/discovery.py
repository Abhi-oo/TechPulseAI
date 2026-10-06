import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database import get_supabase_client
from services.rss_fetcher import ingest_rss_feeds
from agents.discovery import DiscoveryAgent

logger = logging.getLogger("techpulse.routers.discovery")
router = APIRouter(prefix="/api/discovery", tags=["Discovery"])


class CandidateStory(BaseModel):
    title: str
    category: str
    topic_key: str
    relevance_score: float
    matched_keywords: List[str]
    submission_ids: List[str]
    primary_url: str
    summary: str


class DiscoveryRunResponse(BaseModel):
    articles_scanned: int
    new_articles: int
    candidate_stories: List[CandidateStory]
    failed: int


@router.post("/run", response_model=DiscoveryRunResponse)
async def run_discovery_pipeline() -> Dict[str, Any]:
    """
    Triggers the Ingestion + Discovery pipeline:
    1. Fetches and normalizes RSS feeds from configured sources.
    2. Deduplicates articles by URL hash and stores raw articles in 'submissions'.
    3. Runs the Discovery Agent to identify and structure AI/tech candidate stories.
    4. Logs execution metrics and results into 'agent_runs'.
    """
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=500, detail="Database client not configured.")

    start_time = time.time()
    started_at = datetime.now(timezone.utc).isoformat()

    # 1. Initialize audit record in agent_runs
    run_record = {
        "agent_name": "DiscoveryAgent",
        "run_type": "MANUAL_TRIGGER",
        "status": "RUNNING",
        "started_at": started_at,
        "input_payload": {"action": "rss_ingestion_and_discovery"},
        "output_payload": {},
        "tokens_used": 0,
        "duration_ms": 0
    }
    
    agent_run_id = None
    try:
        run_insert = supabase.table("agent_runs").insert(run_record).execute()
        if run_insert.data:
            agent_run_id = run_insert.data[0]["id"]
    except Exception as e:
        logger.error(f"Failed to create agent_run record: {e}")

    try:
        # 2. Ingest RSS feeds
        articles_scanned, new_submissions, failed_feeds = await ingest_rss_feeds()

        # 3. Determine items to evaluate by Discovery Agent
        # If new submissions were found, evaluate those.
        # Otherwise, evaluate recent unprocessed submissions (or latest 50 submissions)
        agent_input = new_submissions
        if not agent_input:
            recent_res = supabase.table("submissions") \
                .select("*") \
                .order("published_at", desc=True) \
                .limit(50) \
                .execute()
            agent_input = recent_res.data or []

        # 4. Run Discovery Agent
        agent = DiscoveryAgent(relevance_threshold=0.45)
        discovery_result = agent.run(agent_input)

        candidate_stories = discovery_result.get("candidate_stories", [])
        duration_ms = int((time.time() - start_time) * 1000)
        completed_at = datetime.now(timezone.utc).isoformat()

        response_payload = {
            "articles_scanned": articles_scanned,
            "new_articles": len(new_submissions),
            "candidate_stories": candidate_stories,
            "failed": failed_feeds
        }

        # 5. Update agent_runs with SUCCESS status
        if agent_run_id:
            supabase.table("agent_runs").update({
                "status": "SUCCESS",
                "completed_at": completed_at,
                "duration_ms": duration_ms,
                "output_payload": {
                    "articles_scanned": articles_scanned,
                    "new_articles": len(new_submissions),
                    "candidate_stories_count": len(candidate_stories),
                    "failed_feeds": failed_feeds
                }
            }).eq("id", agent_run_id).execute()

        return response_payload

    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        completed_at = datetime.now(timezone.utc).isoformat()
        logger.error(f"Discovery pipeline failed: {e}", exc_info=True)

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

        raise HTTPException(status_code=500, detail=f"Discovery pipeline error: {str(e)}")
