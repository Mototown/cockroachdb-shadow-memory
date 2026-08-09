-- ShadowSense schema — production-oriented agentic memory layer
-- Demonstrates CockroachDB Distributed Vector Indexing + transactional safety memory

CREATE EXTENSION IF NOT EXISTS vector;

-- Semantic memory: shadow embeddings for similarity search
CREATE TABLE IF NOT EXISTS shadow_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    embedding VECTOR(1024) NOT NULL,
    sun_azimuth FLOAT NOT NULL,
    sun_elevation FLOAT NOT NULL,
    shadow_length_px FLOAT NOT NULL,
    risk_level STRING NOT NULL CHECK (risk_level IN ('LOW','MEDIUM','HIGH','PRE_APPEARANCE')),
    aisle_id STRING NOT NULL,
    camera_id STRING NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Distributed Vector Index (required CockroachDB tool)
-- Enables fast semantic search over memory at scale without a separate vector store
CREATE INDEX IF NOT EXISTS shadow_embedding_idx
ON shadow_embeddings
USING vector (embedding vector_cosine_ops);

-- Transactional memory: near-miss / safety events
-- SERIALIZABLE isolation is used in application code so concurrent agents cannot
-- silently overwrite the same safety claim.
CREATE TABLE IF NOT EXISTS near_miss_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    forklift_id STRING NOT NULL,
    shadow_id UUID REFERENCES shadow_embeddings(id),
    location STRING NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT now(),
    action_taken STRING NOT NULL,  -- STOP, SLOW, ALERT
    resolved BOOL DEFAULT false
);

CREATE INDEX IF NOT EXISTS near_miss_location_idx
ON near_miss_events (location, timestamp DESC);

-- Agent task / context memory
CREATE TABLE IF NOT EXISTS agent_state (
    agent_id STRING PRIMARY KEY,
    current_task STRING NOT NULL,
    last_seen_pattern_id UUID REFERENCES shadow_embeddings(id),
    last_seen_at TIMESTAMPTZ DEFAULT now(),
    memory_version INT DEFAULT 1
);

-- Example production query patterns used by the agent:
--
-- Semantic retrieval (Distributed Vector Indexing):
--   SELECT id, risk_level, aisle_id, embedding <-> $1 AS distance
--   FROM shadow_embeddings
--   ORDER BY distance
--   LIMIT 5;
--
-- Transactional claim under SERIALIZABLE:
--   BEGIN;
--   SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
--   SELECT ... FOR UPDATE;
--   INSERT INTO near_miss_events ...;
--   COMMIT;
