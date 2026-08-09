# ShadowSense — Safety-Critical Agentic Memory on CockroachDB

**CockroachDB × AWS Hackathon — Build with Agentic Memory**

> Memory is not an afterthought. It is the safety system.

Warehouse forklift accidents often occur at blind corners. Cameras can see a pedestrian’s shadow ~1.5 seconds before the person appears. If the agent forgets that shadow pattern, someone gets hurt. ShadowSense makes **CockroachDB the persistent memory that never loses a safety-critical fact**.

---

## Required Technology Mapping (Hackathon Rules)

### CockroachDB Tools Used (meets “at least 2” requirement)

1. **CockroachDB Distributed Vector Indexing**
   - Stores 1024-dim shadow embeddings directly in CockroachDB.
   - Uses vector similarity search (`embedding <-> $1`) for semantic retrieval of past near-miss patterns.
   - No separate vector database — memory stays consistent with transactional data.

2. **CockroachDB Cloud Managed MCP Server**
   - Intended production path: agents query memory via the managed MCP endpoint (`https://cockroachlabs.cloud/mcp`).
   - Read-only mode + audit logging for safe agent access.
   - Local code currently demonstrates the same queries directly for demo reliability; the MCP path is documented and ready.

3. **ccloud CLI (Agent-Ready)** — used in setup
   - `ccloud_setup.sh` provisions / connects to the cluster using agent-friendly JSON patterns.

### AWS Services Used (meets “at least 1” requirement)

- **Amazon Bedrock** — Titan embeddings for shadow features + Claude for agent reasoning
- **AWS Lambda** — Serverless shadow extraction pipeline
- **Amazon S3** — Raw frame / artifact storage + optional changefeed sink

---

## Why This Is Strong on Judging Criteria

| Criterion | How ShadowSense addresses it |
|-----------|------------------------------|
| **Agentic Memory Design** | Memory *is* the product. Vector + transactional tables store embeddings, near-miss events, and agent state. The agent retrieves similar past patterns and acts (STOP / SLOW / ALERT). |
| **Technical Implementation** | Distributed vector index + SERIALIZABLE transactions + clear MCP path. No toy queries. |
| **Real-World Impact** | Targets real warehouse forklift near-miss prevention using existing cameras. High-stakes domain. |
| **Production Readiness** | SERIALIZABLE isolation prevents silent overwrites, multi-region friendly design, audit-friendly logging, MCP read-only safety. |
| **Creativity & Originality** | Safety-critical memory (forgetting = physical harm) instead of generic chat history. |

---

## Architecture

```
[Warehouse Cameras]
        │
        ▼
[AWS Lambda – Shadow Extractor]
  • Feature extraction
  • Bedrock Titan embedding
  • Write to CockroachDB + S3
        │
        ▼
[CockroachDB Cloud – Persistent Memory Layer]
  • shadow_embeddings (VECTOR + distributed vector index)
  • near_miss_events (transactional, SERIALIZABLE)
  • agent_state
        │
        ▼
[Bedrock Agent / Reasoning Layer]
  • Retrieves similar memories (vector search)
  • Reasons with Claude
  • Acts on the decision (stop forklift, log action)
```

---

## Schema Highlights (`sql/schema.sql`)

- `VECTOR(1024)` column for embeddings
- Distributed vector index for fast semantic search
- `near_miss_events` protected by SERIALIZABLE isolation so two forklifts cannot silently overwrite the same safety claim
- Clear separation of semantic memory vs transactional safety events

---

## Quick Start

```bash
# 1. Provision / connect (see ccloud_setup.sh)
# 2. Apply schema
psql $COCKROACHDB_URL -f sql/schema.sql

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment
cp .env.example .env   # add COCKROACHDB_URL, AWS credentials if needed

# 5. Local agent demo
python src/bedrock_agent.py

# 6. Local Lambda-style extractor demo
python src/lambda_shadow_extractor.py
```

---

## Demo Focus for Judges (< 3 min video)

1. Shadow / near-miss pattern appears
2. Embedding written into CockroachDB vector index
3. Semantic retrieval of similar past events
4. Agent reasons and issues a safety action
5. (Optional but powerful) Concurrent claim of the same aisle under SERIALIZABLE isolation

---

## License

MIT
