# ShadowSense — Submission Checklist (CockroachDB × AWS Hackathon)

## Required technology (must hit these)

### CockroachDB tools (need ≥ 2) — we use:
- [x] Distributed Vector Indexing
- [x] Cloud Managed MCP Server path (documented + same queries)
- [x] ccloud CLI (setup script)

### AWS services (need ≥ 1) — we use:
- [x] Amazon Bedrock
- [x] AWS Lambda
- [x] Amazon S3

## Deliverables
- [x] Public GitHub repo with MIT license
- [x] Clear README
- [x] Schema + agent code demonstrating memory as the product
- [ ] <3 min public video
- [ ] Functional demo notes / connection details if judges need them

## How to run the local demo
```bash
pip install -r requirements.txt
cp .env.example .env          # add COCKROACHDB_URL
python demo.py
```

## Video focus
1. Problem (forgetting shadow patterns = danger)
2. Vector memory write + retrieval
3. Agent decision
4. SERIALIZABLE claim (optional but strong)
