# ShadowSense — Devpost Submission Kit

**Project title:** ShadowSense — Safety-Critical Agentic Memory on CockroachDB

**Tagline:** Memory is not an afterthought. It is the safety system.

**Video:** https://www.youtube.com/watch?v=JoB-8OSoXlQ  
**Repo:** https://github.com/Mototown/cockroachdb-shadow-memory  
**Functional demo:** Run the one-command demo in the repo (see README). Judges can spin up a free CockroachDB Basic cluster in ~2 minutes and execute `python demo.py`.

---

## Ready-to-paste Description (for Devpost)

### Inspiration
Warehouse forklift accidents frequently occur at blind corners. Existing cameras can detect a pedestrian’s shadow approximately 1.5 seconds before the person appears. If an AI agent forgets that pattern, people get hurt. We asked: what if the agent’s memory itself became the safety system?

### What it does
ShadowSense is an agentic application whose long-term memory lives entirely in CockroachDB.

1. An AWS Lambda extracts shadow features from camera images and generates embeddings via Amazon Bedrock Titan.
2. Those embeddings + metadata are stored in CockroachDB using Distributed Vector Indexing.
3. When a new shadow is observed, the agent retrieves similar past patterns via vector search (the same queries work through the CockroachDB Cloud Managed MCP Server).
4. Amazon Bedrock (Claude) reasons over the retrieved memories and decides STOP / SLOW / ALERT.
5. The agent then makes a transactional claim on the aisle using SERIALIZABLE isolation so concurrent agents cannot silently overwrite each other’s safety decisions.

Memory is no longer an afterthought — it is the product.

### How we built it
- CockroachDB schema with `VECTOR(1024)` columns + distributed vector index + transactional tables for near-miss events and agent state.
- Python agent (`src/bedrock_agent.py`) that performs vector retrieval, Bedrock reasoning, and SERIALIZABLE claims.
- Lambda-style extractor that writes both semantic and transactional memory in one flow.
- `ccloud_setup.sh` for agent-ready cluster provisioning on AWS.
- Full local demo that exercises the complete memory loop.

### Challenges we ran into
Making the memory layer production-grade (SERIALIZABLE isolation + MCP audit path) while keeping the demo one-command simple. Balancing mock mode for easy judging with real Bedrock + CockroachDB paths.

### Accomplishments that we're proud of
- True dual-purpose memory (vector + transactional) in a single database with no consistency gaps.
- Safety-critical use case instead of generic chat history.
- Clean mapping to three of the four required CockroachDB tools plus multiple AWS services.
- Short, focused demo video that shows the memory layer working live.

### What we learned
Agentic systems fail when memory is treated as optional. CockroachDB’s combination of distributed SQL, vector indexing, and MCP support lets you treat memory as a first-class, resilient, auditable system of record.

### What's next for ShadowSense
Real camera integration, multi-region deployment for warehouse fleets, and tighter MCP + Agent Skills packaging so any Claude/Cursor agent can adopt the same safety memory pattern.

---

## Tool Identification (paste into the form)

**CockroachDB tools used:**
- Distributed Vector Indexing — primary semantic memory store and retrieval path for shadow patterns.
- Cloud Managed MCP Server — production access path (read-only + audit); demo shows live MCP queries; local code uses identical SQL.
- ccloud CLI (Agent-Ready) — `ccloud_setup.sh` provisions the AWS-hosted cluster, connection strings, networking, and audit log access.

**AWS services used:**
- Amazon Bedrock — Titan embeddings + Claude Haiku reasoning over retrieved memories.
- AWS Lambda — shadow feature extraction and write path into CockroachDB.
- Amazon S3 — image/artifact storage for the extraction pipeline.

---

## Final Checklist

- [x] Agentic application with CockroachDB as persistent memory layer, deployed on AWS
- [x] Agent stores, retrieves, and acts on memory (embeddings + transactional data)
- [x] ≥2 CockroachDB tools (we use 3)
- [x] ≥1 AWS service (we use 3)
- [x] Demo video <3 min, public on YouTube, shows memory layer
- [x] Public repo + MIT license (detectable)
- [x] Clear README + setup + run instructions
- [x] Functional demo (one-command `demo.py` + free CockroachDB Basic cluster)
- [ ] Complete Devpost form (paste description + links + tool mapping above)
- [ ] (Optional) Upload architectural diagram if you generate one

**Deadline reminder:** August 18, 2026 @ 5:00pm EDT
