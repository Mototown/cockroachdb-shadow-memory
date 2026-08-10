#!/usr/bin/env python3
"""One-command local demo for ShadowSense.

Shows the core agentic memory loop:
1. Retrieve similar memories via vector search
2. Reason with the agent
3. Attempt a transactional safety claim (SERIALIZABLE)
"""

import json
import os
from dotenv import load_dotenv

load_dotenv()

from src.bedrock_agent import ShadowMemoryAgent


def main():
    print("=" * 60)
    print("ShadowSense — Agentic Memory Demo")
    print("CockroachDB as the persistent safety memory layer")
    print("=" * 60)

    if not os.getenv("COCKROACHDB_URL"):
        print("\nCOCKROACHDB_URL not set.")
        print("Set it in .env or export it, then re-run.")
        print("For a pure mock walk-through you can still read the code paths.")
        return

    agent = ShadowMemoryAgent()

    current = {
        "sun_azimuth": 135.0,
        "sun_elevation": 35.0,
        "shadow_length_px": 125.0,
        "aisle_id": "aisle_3",
    }

    mock_embedding = [0.1] * 1024

    print("\n1. Querying CockroachDB memory (Distributed Vector Indexing)...")
    memories = agent.query_similar_memories(mock_embedding)
    print(f"   Retrieved {len(memories)} similar memories")

    print("\n2. Agent reasoning over memory...")
    decision = agent.reason(memories, current)
    print("   Decision:")
    print(json.dumps(decision, indent=4))

    print("\n3. Transactional aisle claim (SERIALIZABLE isolation)...")
    result = agent.claim_aisle_transactional(
        forklift_id="forklift_1",
        shadow_id="00000000-0000-0000-0000-000000000001",
        location="aisle_3",
    )
    print("   Result:", result)

    print("\nDemo complete. Memory layer exercised.")


if __name__ == "__main__":
    main()
