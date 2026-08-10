# ShadowSense — Safety-Critical Agentic Memory on CockroachDB

**CockroachDB × AWS Hackathon — Build with Agentic Memory**

> Memory is not an afterthought. It is the safety system.

Warehouse forklift accidents often happen at blind corners. Cameras can see a pedestrian’s shadow ~1.5 seconds before the person appears. If the agent forgets that pattern, someone gets hurt. ShadowSense makes **CockroachDB the persistent memory that never loses a safety-critical fact**.

---

## Required Technology Mapping

### CockroachDB Tools (meets “at least 2”)

1. **Distributed Vector Indexing** — stores and searches shadow embeddings for similar near-miss patterns  
2. **Cloud Managed MCP Server** — production path for safe agent access to memory (read-only + audit)  
3. **ccloud CLI** — used in setup (`ccloud_setup.sh`)

### AWS Services (meets “at least 1”)

- **Amazon Bedrock** — embeddings + agent reasoning  
- **AWS Lambda** — shadow extraction pipeline  
- **Amazon S3** — artifact storage  

---

## Why this scores well

| Criterion | How we address it |
|-----------|-------------------|
| Agentic Memory Design | Memory *is* the product (vector + transactional tables) |
| Technical Implementation | Vector index + SERIALIZABLE + MCP path |
| Real-World Impact | Warehouse near-miss prevention using existing cameras |
| Production Readiness | Isolation, audit-friendly design, multi-region friendly |
| Creativity | Safety-critical memory instead of generic chat history |

---

## Quick start

```bash
git clone https://github.com/Mototown/cockroachdb-shadow-memory.git
cd cockroachdb-shadow-memory
pip install -r requirements.txt
cp .env.example .env          # set COCKROACHDB_URL

# Apply schema (once)
# psql $COCKROACHDB_URL -f sql/schema.sql

# Run the one-command demo
python demo.py
```

---

## Project layout

```
cockroachdb-shadow-memory/
├── demo.py                      # One-command demo
├── src/
│   ├── bedrock_agent.py         # Memory retrieval + reasoning + SERIALIZABLE claim
│   └── lambda_shadow_extractor.py
├── sql/schema.sql               # Vector + transactional memory tables
├── ccloud_setup.sh               # Agent-ready cluster setup
├── SUBMISSION.md
└── README.md
```

---

## License

MIT
