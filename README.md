# ShadowSense — Safety-Critical Agentic Memory on CockroachDB

**CockroachDB × AWS Hackathon — Build with Agentic Memory**

> Memory is not an afterthought. It is the safety system.

Warehouse forklift accidents often happen at blind corners. Cameras can see a pedestrian’s shadow ~1.5 seconds before the person appears. If the agent forgets that pattern, someone gets hurt. **ShadowSense makes CockroachDB the persistent memory that never loses a safety-critical fact.**

**Demo video (2:03):** [ShadowSense – CockroachDB Shadow Memory demo](https://www.youtube.com/watch?v=JoB-8OSoXlQ)

---

## Functional Demo (for Judges)

The easiest way for judges to evaluate the project:

```bash
git clone https://github.com/Mototown/cockroachdb-shadow-memory.git
cd cockroachdb-shadow-memory
pip install -r requirements.txt
streamlit run app.py
```

The Streamlit app (`app.py`) runs a complete, interactive demonstration of the agentic memory loop:

1. Semantic retrieval via **Distributed Vector Indexing**
2. Agent reasoning over the retrieved memories
3. **SERIALIZABLE** transactional claim on the aisle

It works fully in high-fidelity **mock mode** (no credentials required) so judges can evaluate immediately.  
A checkbox also allows connecting to a real CockroachDB cluster if a connection string is available.

The same SQL shown in the demo is the exact query pattern used with the **Cloud Managed MCP Server** in production.

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
- Demo uses the exact same SQL the agent would issue through MCP.

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

## Local CLI Demo (optional)

```bash
cp .env.example .env          # set COCKROACHDB_URL if desired
python demo.py
```

Set `MOCK_AWS=1` to run without real Bedrock credentials.

---

## Project layout

```
cockroachdb-shadow-memory/
├── app.py                           # Streamlit functional demo (primary for judges)
├── demo.py                          # One-command CLI demo
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
