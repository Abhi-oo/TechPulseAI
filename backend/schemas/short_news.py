from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


def _trim_to_word_limit(text: str, max_words: int = 30) -> str:
    """Safely trims text to specified word count without cutting mid-word."""
    words = text.strip().split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).rstrip(".,;:-") + "..."


class IntelligenceCard(BaseModel):
    """
    Concise intelligence card representation for a canonical tech story.
    Enforces <= 30 words per field to deliver high-signal executive briefings.
    """
    what: str = Field(description="Direct factual explanation of the event, <= 30 words.")
    why_it_matters: str = Field(description="Engineering / technical significance, <= 30 words.")
    impact: str = Field(description="Ecosystem / market consequences, <= 30 words.")

    @field_validator("what", mode="after")
    @classmethod
    def validate_what_length(cls, v: str) -> str:
        return _trim_to_word_limit(v, max_words=30)

    @field_validator("why_it_matters", mode="after")
    @classmethod
    def validate_why_length(cls, v: str) -> str:
        return _trim_to_word_limit(v, max_words=30)

    @field_validator("impact", mode="after")
    @classmethod
    def validate_impact_length(cls, v: str) -> str:
        return _trim_to_word_limit(v, max_words=30)


class RankingComponents(BaseModel):
    """Individual normalized 0-100 components contributing to the ranking score."""
    recency_norm: float = Field(ge=0.0, le=100.0)
    importance_norm: float = Field(ge=0.0, le=100.0)
    impact_norm: float = Field(ge=0.0, le=100.0)
    confidence_norm: float = Field(ge=0.0, le=100.0)
    ranking_score: float = Field(ge=0.0, le=100.0)
    age_hours: float
    explanation: str


class ProcessedStorySummary(BaseModel):
    """Summary record for a story updated with intelligence fields and ranking."""
    story_id: str
    title: str
    category: str
    what: str
    why_it_matters: str
    impact: str
    confidence: int
    ranking_score: float
    status: str
