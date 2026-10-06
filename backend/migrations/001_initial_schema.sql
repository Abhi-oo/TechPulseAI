-- ============================================================================
-- TechPulse AI: Milestone 1 Database Migration
-- Target Engine: Supabase PostgreSQL
-- ============================================================================

-- 1. Ensure pgcrypto extension is enabled for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ----------------------------------------------------------------------------
-- Reusable updated_at Trigger Function
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ----------------------------------------------------------------------------
-- 1. Table: sources
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    domain VARCHAR(255) UNIQUE NOT NULL,
    feed_url TEXT NOT NULL,
    feed_type VARCHAR(50) DEFAULT 'rss' NOT NULL,
    tier VARCHAR(30) DEFAULT 'STANDARD' NOT NULL, -- 'PRIMARY', 'VERIFIED_NEWS', 'AGGREGATOR'
    reliability_weight FLOAT DEFAULT 1.0 NOT NULL,
    is_active BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

DROP TRIGGER IF EXISTS trg_sources_updated_at ON sources;
CREATE TRIGGER trg_sources_updated_at
    BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- 2. Table: stories (The Canonical Intelligence Unit)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS stories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(300) NOT NULL,
    slug VARCHAR(350) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,
    what TEXT NOT NULL,
    why_it_matters TEXT NOT NULL,
    impact TEXT NOT NULL,
    confidence INT DEFAULT 50 NOT NULL CHECK (confidence BETWEEN 0 AND 100),
    importance_score FLOAT DEFAULT 5.0 NOT NULL,
    ranking_score FLOAT DEFAULT 0.0 NOT NULL,
    status VARCHAR(30) DEFAULT 'DRAFT' NOT NULL, -- 'DRAFT', 'VERIFIED', 'PUBLISHED', 'ARCHIVED'
    first_seen_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    last_updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    update_count INT DEFAULT 0 NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

DROP TRIGGER IF EXISTS trg_stories_updated_at ON stories;
CREATE TRIGGER trg_stories_updated_at
    BEFORE UPDATE ON stories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- 3. Table: submissions (Raw Scraped Items)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES sources(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    url_hash VARCHAR(64) UNIQUE NOT NULL,
    author VARCHAR(255),
    raw_content TEXT NOT NULL,
    cleaned_content TEXT,
    published_at TIMESTAMPTZ NOT NULL,
    processed BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

DROP TRIGGER IF EXISTS trg_submissions_updated_at ON submissions;
CREATE TRIGGER trg_submissions_updated_at
    BEFORE UPDATE ON submissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- 4. Table: story_sources (M:N Association & Citation Registry)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS story_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    submission_id UUID REFERENCES submissions(id) ON DELETE SET NULL,
    article_url TEXT NOT NULL,
    article_title TEXT NOT NULL,
    is_primary_origin BOOLEAN DEFAULT false NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    CONSTRAINT uq_story_sources UNIQUE (story_id, article_url)
);

DROP TRIGGER IF EXISTS trg_story_sources_updated_at ON story_sources;
CREATE TRIGGER trg_story_sources_updated_at
    BEFORE UPDATE ON story_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- 5. Table: story_updates (Chronological Timeline Evolution)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS story_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    submission_id UUID REFERENCES submissions(id) ON DELETE SET NULL,
    headline VARCHAR(300) NOT NULL,
    summary TEXT NOT NULL,
    update_type VARCHAR(50) DEFAULT 'DEVELOPMENT' NOT NULL, -- 'ANNOUNCEMENT', 'CONFIRMATION', 'BENCHMARK', 'TECHNICAL_DETAILS', 'OFFICIAL_RESPONSE'
    source_name VARCHAR(100),
    source_url TEXT,
    occurred_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

DROP TRIGGER IF EXISTS trg_story_updates_updated_at ON story_updates;
CREATE TRIGGER trg_story_updates_updated_at
    BEFORE UPDATE ON story_updates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- 6. Table: claims (Extracted Factual Claims & Corroboration)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    story_id UUID NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    claim_text TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'UNCONFIRMED' NOT NULL, -- 'CONFIRMED', 'DISPUTED', 'UNCONFIRMED'
    corroboration_count INT DEFAULT 1 NOT NULL,
    evidence JSONB DEFAULT '[]'::jsonb NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

DROP TRIGGER IF EXISTS trg_claims_updated_at ON claims;
CREATE TRIGGER trg_claims_updated_at
    BEFORE UPDATE ON claims
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- 7. Table: agent_runs (Telemetry & Audit Logs)
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agent_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(100) NOT NULL,
    run_type VARCHAR(50) NOT NULL,               -- 'SCHEDULED', 'MANUAL_TRIGGER', 'EVENT_TRIGGER'
    status VARCHAR(30) DEFAULT 'RUNNING' NOT NULL, -- 'RUNNING', 'SUCCESS', 'FAILED'
    story_id UUID REFERENCES stories(id) ON DELETE SET NULL,
    input_payload JSONB DEFAULT '{}'::jsonb NOT NULL,
    output_payload JSONB DEFAULT '{}'::jsonb NOT NULL,
    tokens_used INT DEFAULT 0 NOT NULL,
    duration_ms INT DEFAULT 0 NOT NULL,
    error_message TEXT,
    started_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT now() NOT NULL
);

DROP TRIGGER IF EXISTS trg_agent_runs_updated_at ON agent_runs;
CREATE TRIGGER trg_agent_runs_updated_at
    BEFORE UPDATE ON agent_runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ----------------------------------------------------------------------------
-- Indexes for High Performance & Query Optimization
-- ----------------------------------------------------------------------------
-- Feed Queries
CREATE INDEX IF NOT EXISTS idx_stories_feed_ranking ON stories(status, ranking_score DESC, last_updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_stories_category ON stories(category);
CREATE INDEX IF NOT EXISTS idx_stories_slug ON stories(slug);

-- Ingestion & Deduplication
CREATE INDEX IF NOT EXISTS idx_submissions_url_hash ON submissions(url_hash);
CREATE INDEX IF NOT EXISTS idx_submissions_processed ON submissions(processed, published_at DESC);

-- Story-Source Relationships
CREATE INDEX IF NOT EXISTS idx_story_sources_story_id ON story_sources(story_id);
CREATE INDEX IF NOT EXISTS idx_story_sources_source_id ON story_sources(source_id);
CREATE INDEX IF NOT EXISTS idx_story_sources_submission_id ON story_sources(submission_id);

-- Timeline Evolution
CREATE INDEX IF NOT EXISTS idx_story_updates_story_timeline ON story_updates(story_id, occurred_at ASC);

-- Verification Claims
CREATE INDEX IF NOT EXISTS idx_claims_story_id ON claims(story_id);

-- Agent Telemetry
CREATE INDEX IF NOT EXISTS idx_agent_runs_telemetry ON agent_runs(agent_name, status, started_at DESC);
