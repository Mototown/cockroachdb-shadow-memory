-- schema.sql - Production-grade memory layer
-- Uses Distributed Vector Indexing + SERIALIZABLE for safety-critical memory

-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Table 1: Shadow embeddings - semantic memory
-- Stores 1024-dim embeddings from Bedrock Titan
CREATE TABLE shadow_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    embedding VECTOR(1024) NOT NULL,
    sun_azimuth FLOAT NOT NULL,
    sun_elevation FLOAT NOT NULL,
    shadow_length_px FLOAT NOT NULL,
    risk_level STRING NOT NULL, -- LOW, MEDIUM, HIGH, PRE_APPEARANCE
    aisle_id STRING NOT NULL,
    camera_id STRING NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    -- For transactional consistency with near_miss_events
    CONSTRAINT risk_check CHECK (risk_level IN ('LOW','MEDIUM','HIGH','PRE_APPEARANCE'))
);

-- Distributed Vector Index - key CockroachDB tool
-- Fast semantic search as data grows, no separate vector store
CREATE VECTOR INDEX shadow_embedding_idx ON shadow_embeddings (embedding)
WITH (metric = 'cosine_distance');

-- Table 2: Near-miss events - transactional memory
-- Must never lose a fact - SERIALIZABLE
CREATE TABLE near_miss_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    forklift_id STRING NOT NULL,
    shadow_id UUID REFERENCES shadow_embeddings(id),
    location STRING NOT NULL, -- aisle_3_blind_corner
    timestamp TIMESTAMPTZ DEFAULT now(),
    action_taken STRING NOT NULL, -- STOP, SLOW, ALERT
    resolved BOOL DEFAULT false,
    -- Prevent two forklifts claiming same aisle at same time
    CONSTRAINT unique_location_time UNIQUE (location, timestamp)
);

-- Table 3: Agent state - task memory
CREATE TABLE agent_state (
    agent_id STRING PRIMARY KEY,
    current_task STRING NOT NULL,
    last_seen_pattern_id UUID REFERENCES shadow_embeddings(id),
    last_seen_at TIMESTAMPTZ DEFAULT now(),
    memory_version INT DEFAULT 1
);

-- Index for fast location queries
CREATE INDEX near_miss_location_idx ON near_miss_events (location, timestamp DESC);

-- Example production query: Semantic search for similar shadow pattern
-- This is what Bedrock agent calls via MCP Server
-- SELECT id, sun_azimuth, risk_level FROM shadow_embeddings ORDER BY embedding <-> $1 LIMIT 5;

-- Example transactional query: Claim aisle with SERIALIZABLE
-- BEGIN;
-- SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- SELECT * FROM near_miss_events WHERE location='aisle_3' AND timestamp > now() - INTERVAL '5 seconds' FOR UPDATE;
-- INSERT INTO near_miss_events (forklift_id, shadow_id, location, action_taken) VALUES ('forklift_1', $1, 'aisle_3', 'STOP');
-- COMMIT;

-- Seed data for demo
INSERT INTO shadow_embeddings (embedding, sun_azimuth, sun_elevation, shadow_length_px, risk_level, aisle_id, camera_id)
VALUES 
  (random_vector(1024), 135.0, 35.0, 120.5, 'HIGH', 'aisle_3', 'cam_1'),
  (random_vector(1024), 180.0, 70.0, 20.1, 'LOW', 'aisle_3', 'cam_1'),
  (random_vector(1024), 225.0, 25.0, 180.3, 'PRE_APPEARANCE', 'aisle_3', 'cam_2');
