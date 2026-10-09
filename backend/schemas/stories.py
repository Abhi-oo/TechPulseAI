from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class StorySourceItem(BaseModel):
    id: str
    story_id: str
    source_id: Optional[str] = None
    submission_id: Optional[str] = None
    article_url: str
    article_title: str
    is_primary_origin: bool = False


class ClaimItem(BaseModel):
    id: str
    story_id: str
    claim_text: str
    status: str
    corroboration_count: int = 1
    evidence: List[Dict[str, Any]] = Field(default_factory=list)


class StoryTimelineEventItem(BaseModel):
    id: str
    story_id: str
    submission_id: Optional[str] = None
    headline: str
    summary: str
    update_type: str
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    occurred_at: str


class StoryFeedItem(BaseModel):
    id: str
    title: str
    slug: str
    category: str
    what: str
    why_it_matters: str
    impact: str
    confidence: int
    importance_score: float
    ranking_score: float
    status: str
    first_seen_at: str
    last_updated_at: str
    update_count: int
    sources: List[StorySourceItem] = Field(default_factory=list)


class StoryFeedResponse(BaseModel):
    total: int
    stories: List[StoryFeedItem]


class StoryDetailResponse(BaseModel):
    id: str
    title: str
    slug: str
    category: str
    what: str
    why_it_matters: str
    impact: str
    confidence: int
    importance_score: float
    ranking_score: float
    status: str
    first_seen_at: str
    last_updated_at: str
    update_count: int
    sources: List[StorySourceItem] = Field(default_factory=list)
    claims: List[ClaimItem] = Field(default_factory=list)
    timeline: List[StoryTimelineEventItem] = Field(default_factory=list)


class PlatformStatsResponse(BaseModel):
    total_stories: int
    verified_stories: int
    total_claims: int
    total_sources: int
    average_confidence: float
    categories: Dict[str, int]
