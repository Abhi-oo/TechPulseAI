import re
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query

from database import get_supabase_client
from schemas.stories import (
    StoryFeedResponse,
    StoryFeedItem,
    StoryDetailResponse,
    StorySourceItem,
    ClaimItem,
    StoryTimelineEventItem,
    PlatformStatsResponse
)

logger = logging.getLogger("techpulse.routers.stories")
router = APIRouter(prefix="/api", tags=["Stories & Feed"])

UUID_REGEX = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)


@router.get("/stories", response_model=StoryFeedResponse)
async def list_stories(
    category: Optional[str] = Query(default=None, description="Filter by category (e.g. 'LLMs & GenAI', 'Hardware & Silicon')"),
    sort_by: str = Query(default="rank", pattern="^(rank|recent|confidence)$", description="Sorting field: 'rank', 'recent', or 'confidence'"),
    search: Optional[str] = Query(default=None, description="Search query string matching title"),
    limit: int = Query(default=30, ge=1, le=100, description="Page limit"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination")
) -> Dict[str, Any]:
    """
    Returns paginated canonical stories from Supabase with attached source citations.
    Supports filtering by category, search by title, and sorting by rank, recency, or confidence.
    """
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=500, detail="Database client is not configured.")

    try:
        # Build query on stories table
        query = supabase.table("stories").select("*", count="exact")

        if category and category.lower() != "for you" and category.lower() != "all":
            query = query.eq("category", category)

        if search and search.strip():
            query = query.ilike("title", f"%{search.strip()}%")

        # Apply sorting
        if sort_by == "recent":
            query = query.order("last_updated_at", desc=True)
        elif sort_by == "confidence":
            query = query.order("confidence", desc=True).order("ranking_score", desc=True)
        else:  # default "rank"
            query = query.order("ranking_score", desc=True).order("last_updated_at", desc=True)

        # Pagination
        query = query.range(offset, offset + limit - 1)
        res = query.execute()

        raw_stories = res.data or []
        total_count = res.count if res.count is not None else len(raw_stories)

        # Batch query sources for all returned story IDs
        story_ids = [s["id"] for s in raw_stories]
        sources_by_story: Dict[str, List[Dict[str, Any]]] = {sid: [] for sid in story_ids}

        if story_ids:
            src_res = supabase.table("story_sources") \
                .select("id, story_id, source_id, submission_id, article_url, article_title, is_primary_origin") \
                .in_("story_id", story_ids) \
                .execute()
            for src in (src_res.data or []):
                sid = src.get("story_id")
                if sid in sources_by_story:
                    sources_by_story[sid].append(src)

        feed_items = []
        for s in raw_stories:
            sid = s["id"]
            feed_items.append({
                "id": sid,
                "title": s.get("title", ""),
                "slug": s.get("slug", ""),
                "category": s.get("category", "Technology"),
                "what": s.get("what", ""),
                "why_it_matters": s.get("why_it_matters", ""),
                "impact": s.get("impact", ""),
                "confidence": s.get("confidence", 50),
                "importance_score": float(s.get("importance_score") or 5.0),
                "ranking_score": float(s.get("ranking_score") or 0.0),
                "status": s.get("status", "DRAFT"),
                "first_seen_at": s.get("first_seen_at") or "",
                "last_updated_at": s.get("last_updated_at") or "",
                "update_count": s.get("update_count") or 0,
                "sources": sources_by_story.get(sid, [])
            })

        return {
            "total": total_count,
            "stories": feed_items
        }

    except Exception as e:
        logger.error(f"Error listing stories: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch stories: {str(e)}")


@router.get("/stories/{story_id_or_slug}", response_model=StoryDetailResponse)
async def get_story_detail(story_id_or_slug: str) -> Dict[str, Any]:
    """
    Returns full story dossier by UUID or slug, including verified claims with evidence
    and chronological timeline evolution events.
    """
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=500, detail="Database client is not configured.")

    try:
        # Determine whether input is UUID or slug
        is_uuid = bool(UUID_REGEX.match(story_id_or_slug.strip()))
        query = supabase.table("stories").select("*")
        if is_uuid:
            query = query.eq("id", story_id_or_slug.strip())
        else:
            query = query.eq("slug", story_id_or_slug.strip())

        res = query.execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Story not found")

        story = res.data[0]
        story_id = story["id"]

        # Fetch linked sources
        src_res = supabase.table("story_sources") \
            .select("id, story_id, source_id, submission_id, article_url, article_title, is_primary_origin") \
            .eq("story_id", story_id) \
            .execute()
        sources = src_res.data or []

        # Fetch verified claims
        claims_res = supabase.table("claims") \
            .select("id, story_id, claim_text, status, corroboration_count, evidence") \
            .eq("story_id", story_id) \
            .execute()
        claims = claims_res.data or []

        # Fetch timeline events
        timeline_res = supabase.table("story_updates") \
            .select("id, story_id, submission_id, headline, summary, update_type, source_name, source_url, occurred_at") \
            .eq("story_id", story_id) \
            .order("occurred_at", desc=False) \
            .execute()
        timeline = timeline_res.data or []

        return {
            "id": story_id,
            "title": story.get("title", ""),
            "slug": story.get("slug", ""),
            "category": story.get("category", "Technology"),
            "what": story.get("what", ""),
            "why_it_matters": story.get("why_it_matters", ""),
            "impact": story.get("impact", ""),
            "confidence": story.get("confidence", 50),
            "importance_score": float(story.get("importance_score") or 5.0),
            "ranking_score": float(story.get("ranking_score") or 0.0),
            "status": story.get("status", "DRAFT"),
            "first_seen_at": story.get("first_seen_at") or "",
            "last_updated_at": story.get("last_updated_at") or "",
            "update_count": story.get("update_count") or 0,
            "sources": sources,
            "claims": claims,
            "timeline": timeline
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching story detail for {story_id_or_slug}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch story detail: {str(e)}")


@router.get("/stories/{story_id}/timeline", response_model=List[StoryTimelineEventItem])
async def get_story_timeline(story_id: str) -> List[Dict[str, Any]]:
    """Returns chronological timeline updates for a specific story."""
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=500, detail="Database client is not configured.")

    try:
        timeline_res = supabase.table("story_updates") \
            .select("id, story_id, submission_id, headline, summary, update_type, source_name, source_url, occurred_at") \
            .eq("story_id", story_id) \
            .order("occurred_at", desc=False) \
            .execute()
        return timeline_res.data or []
    except Exception as e:
        logger.error(f"Error fetching timeline for story {story_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch timeline: {str(e)}")


@router.get("/stats", response_model=PlatformStatsResponse)
async def get_platform_stats() -> Dict[str, Any]:
    """
    Returns live platform telemetry: total canonical stories, verified stories,
    total claims, active sources, average confidence, and category breakdown.
    """
    supabase = get_supabase_client()
    if not supabase:
        raise HTTPException(status_code=500, detail="Database client is not configured.")

    try:
        # 1. Stories count & verified count
        stories_res = supabase.table("stories").select("id, confidence, category, status").execute()
        all_stories = stories_res.data or []
        total_stories = len(all_stories)
        verified_stories = sum(1 for s in all_stories if s.get("status") == "VERIFIED")

        # Average confidence
        avg_confidence = (
            round(sum(s.get("confidence", 50) for s in all_stories) / total_stories, 1)
            if total_stories > 0 else 0.0
        )

        # Categories distribution
        categories_dict: Dict[str, int] = {}
        for s in all_stories:
            cat = s.get("category", "Technology")
            categories_dict[cat] = categories_dict.get(cat, 0) + 1

        # 2. Total claims count
        claims_res = supabase.table("claims").select("count", count="exact").execute()
        total_claims = claims_res.count or 0

        # 3. Active sources count
        sources_res = supabase.table("sources").select("count", count="exact").eq("is_active", True).execute()
        total_sources = sources_res.count or 0

        return {
            "total_stories": total_stories,
            "verified_stories": verified_stories,
            "total_claims": total_claims,
            "total_sources": total_sources,
            "average_confidence": avg_confidence,
            "categories": categories_dict
        }

    except Exception as e:
        logger.error(f"Error fetching platform stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch platform stats: {str(e)}")
