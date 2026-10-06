from typing import List, Optional
from pydantic import BaseModel, Field


class ExtractedClaim(BaseModel):
    """Represents a factual claim extracted from candidate articles."""
    claim_text: str = Field(description="The concrete, factual claim being asserted.")
    claim_type: str = Field(default="FACT", description="Type of claim (e.g. BENCHMARK, ARCHITECTURE, RELEASE, POLICY).")
    needed_evidence: str = Field(default="", description="What specific evidence would confirm or falsify this claim.")


class ClaimEvidence(BaseModel):
    """Evidence snippet evaluated against a claim."""
    source_name: str
    source_url: str
    quote: str
    stance: str = Field(description="SUPPORTS, CONTRADICTS, or NEUTRAL")


class VerifiedClaimResult(BaseModel):
    """The result of cross-referencing a claim across available sources."""
    claim_text: str
    status: str = Field(description="CONFIRMED, DISPUTED, or UNCONFIRMED")
    corroboration_count: int = 1
    evidence: List[ClaimEvidence] = Field(default_factory=list)


class StoryNarrative(BaseModel):
    """The synthesized technical narrative triad for a canonical story."""
    title: str = Field(description="Clean, informative canonical headline.")
    category: str = Field(description="Classified technology sector.")
    what: str = Field(description="Factual description of what occurred.")
    why_it_matters: str = Field(description="Technical significance and engineering depth.")
    impact: str = Field(description="Broader ecosystem and market consequences.")


class ConfidenceBreakdown(BaseModel):
    """Transparent and explainable confidence score breakdown."""
    source_reliability_score: float
    primary_source_bonus: float
    corroboration_score: float
    agreement_score: float
    evidence_depth_score: float
    total_confidence: int = Field(ge=0, le=100)
    explanation: str


class ResearchProcessResult(BaseModel):
    """Output summary for researching a single candidate story."""
    story_id: Optional[str] = None
    title: str
    category: str
    confidence: int
    claims_count: int
    claims_confirmed: int
    claims_disputed: int
    claims_unconfirmed: int
    sources_linked: int
    status: str
