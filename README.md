# ShadowSense — Safety-Critical Agentic Memory on CockroachDB

**CockroachDB × AWS Hackathon — Build with Agentic Memory**

> Memory is not an afterthought. It is the safety system.

Warehouse forklift accidents often happen at blind corners. Cameras can see a pedestrian’s shadow ~1.5 seconds before the person appears. If the agent forgets that pattern, someone gets hurt. **ShadowSense makes CockroachDB the persistent memory that never loses a safety-critical fact.**

**Demo video (2:03):** [ShadowSense – CockroachDB Shadow Memory demo](https://www.youtube.com/watch?v=JoB-8OSoXlQ)

---

## Architecture

```
Camera / Image → AWS Lambda (feature extract) → Amazon Bedrock Titan (embedding)
                                                      ↓
                                         CockroachDB (Vector + Transactional Memory)
                                                      ↓
                              Agent (Bedrock Claude) ←→ MCP Server / direct SQL
                                                      ↓
                                         Action: STOP / SLOW / ALERT  +  SERIALIZABLE claim
```

**Key design choices**
- One database for both semantic (vector) and transactional safety memory — no consistency gaps.
- SERIALIZABLE isolation so concurrent agents cannot silently overwrite the same aisle claim.
- Production path uses CockroachDB Cloud Managed MCP Server (read-only + full audit).
- Local demo uses the exact same SQL the agent would issue through MCP.

---

## Required Technology Mapping

### CockroachDB Tools (we use 3 of the 4 required)

| Tool | How the agent uses it |
|------|-----------------------|
| **Distributed Vector Indexing** | Stores shadow embeddings and retrieves similar near-miss patterns with `embedding <-> query` + vector index |
| **Cloud Managed MCP Server** | Intended production path for safe, audited agent access to memory (demo shows live MCP queries) |
| **ccloud CLI (Agent-Ready)** | `ccloud_setup.sh` provisions the AWS cluster, obtains connection strings, manages networking & audit logs |

### AWS Services

| Service | Role |
|---------|------|
| **Amazon Bedrock** | Titan embeddings + Claude Haiku reasoning over retrieved memories |
| **AWS Lambda** | Shadow feature extraction pipeline (image → features → embedding → write to CockroachDB) |
| **Amazon S3** | Artifact / image storage for the extraction pipeline |

---

## Why this scores well on the judging criteria

| Criterion | How ShadowSense addresses it |
|-----------|------------------------------|
| **Agentic Memory Design** | Memory *is* the product — vector patterns + transactional claims, not an afterthought |
| **Technical Implementation** | Real vector index, SERIALIZABLE isolation, MCP-ready queries, ccloud automation |
| **Real-World Impact** | Prevents warehouse near-misses using existing cameras; safety-critical use case |
| **Production Readiness** | Isolation levels, audit path via MCP, multi-region friendly design, clear failure modes |
| **Creativity & Originality** | Safety-critical shadow memory instead of generic chat history |

---

## Quick start (functional demo)

```bash
git clone https://github.com/Mototown/cockroachdb-shadow-memory.git
cd cockroachdb-shadow-memory
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set COCKROACHDB_URL (create a free CockroachDB Basic cluster in ~2 minutes)

# Apply schema once
psql "$COCKROACHDB_URL" -f sql/schema.sql

# Run the one-command demo (exercises vector search → reason → SERIALIZABLE claim)
python demo.py
```

Set `MOCK_AWS=1` in `.env` to run without real Bedrock credentials (still fully exercises the CockroachDB memory layer).

---

## Project layout

```
cockroachdb-shadow-memory/
├── demo.py                          # One-command demo of the full memory loop
├── src/
│   ├── bedrock_agent.py             # Vector retrieval + Bedrock reasoning + SERIALIZABLE claim
│   └── lambda_shadow_extractor.py   # AWS Lambda-style extractor → CockroachDB
├── sql/schema.sql                   # Vector + transactional tables + indexes
├── ccloud_setup.sh                   # Agent-ready cluster provisioning
├── SUBMISSION.md                    # Devpost-ready notes
└── README.md
```

---

## License

MIT
