export interface StorySource {
  id: string;
  story_id: string;
  source_id?: string | null;
  submission_id?: string | null;
  article_url: string;
  article_title: string;
  is_primary_origin: boolean;
}

export interface ClaimEvidence {
  source_name: string;
  source_url: string;
  quote: string;
  stance: "SUPPORTS" | "CONTRADICTS" | "NEUTRAL" | string;
}

export interface ClaimItem {
  id: string;
  story_id: string;
  claim_text: string;
  status: "CONFIRMED" | "DISPUTED" | "UNCONFIRMED" | string;
  corroboration_count: number;
  evidence: ClaimEvidence[];
}

export interface StoryTimelineEvent {
  id: string;
  story_id: string;
  submission_id?: string | null;
  headline: string;
  summary: string;
  update_type: string;
  source_name?: string | null;
  source_url?: string | null;
  occurred_at: string;
}

export interface Story {
  id: string;
  title: string;
  slug: string;
  category: string;
  what: string;
  why_it_matters: string;
  impact: string;
  confidence: number;
  importance_score: number;
  ranking_score: number;
  status: string;
  first_seen_at: string;
  last_updated_at: string;
  update_count: number;
  sources: StorySource[];
}

export interface StoryFeedResponse {
  total: number;
  stories: Story[];
}

export interface StoryDetailResponse extends Story {
  claims: ClaimItem[];
  timeline: StoryTimelineEvent[];
}

export interface PlatformStats {
  total_stories: number;
  verified_stories: number;
  total_claims: number;
  total_sources: number;
  average_confidence: number;
  categories: Record<string, number>;
}
