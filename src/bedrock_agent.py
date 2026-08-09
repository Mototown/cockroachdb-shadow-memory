"""
ShadowSense agent — uses CockroachDB as the persistent memory layer.

Demonstrates:
- Distributed Vector Indexing for semantic memory retrieval
- SERIALIZABLE transactions for safety-critical claims
- Path to CockroachDB Cloud Managed MCP Server for production agent access
- Amazon Bedrock for reasoning
"""

import os
import json
from typing import Any, List, Optional

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_SERIALIZABLE
from dotenv import load_dotenv

load_dotenv()

try:
    import boto3
except ImportError:
    boto3 = None


class ShadowMemoryAgent:
    """Agent whose memory is CockroachDB."""

    def __init__(self):
        self.cockroach_url = os.getenv("COCKROACHDB_URL")
        if not self.cockroach_url:
            raise RuntimeError("COCKROACHDB_URL is required")

        self.bedrock = None
        if boto3 and os.getenv("MOCK_AWS") != "1":
            self.bedrock = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-west-2"))

    def query_similar_memories(self, query_embedding: List[float], limit: int = 5) -> List[Any]:
        """
        Semantic memory retrieval via CockroachDB Distributed Vector Indexing.

        In production this query is intended to be issued through the
        CockroachDB Cloud Managed MCP Server (read-only + audit logging).
        For local demos we execute the same SQL directly.
        """
        conn = psycopg2.connect(self.cockroach_url)
        try:
            with conn.cursor() as cur:
                # Vector distance operator — core of Distributed Vector Indexing
                cur.execute(
                    """
                    SELECT id, sun_azimuth, sun_elevation, risk_level, aisle_id,
                           embedding <-> %s::vector AS distance
                    FROM shadow_embeddings
                    ORDER BY distance ASC
                    LIMIT %s
                    """,
                    (query_embedding, limit),
                )
                return cur.fetchall()
        finally:
            conn.close()

    def reason(self, similar_memories: List[Any], current_features: dict) -> dict:
        """Use Bedrock (Claude) to reason over retrieved memory."""
        prompt = f"""
You are a warehouse safety agent. Your long-term memory is CockroachDB.

Current shadow features:
{json.dumps(current_features, indent=2)}

Similar past memories retrieved via vector search:
{similar_memories}

Decide the correct action. Prefer safety.
Respond with JSON only:
{{"action": "STOP|SLOW|ALERT", "reasoning": "...", "confidence": 0.0-1.0}}
""".strip()

        if self.bedrock is None or os.getenv("MOCK_AWS") == "1":
            return {
                "action": "STOP",
                "reasoning": "Memory contains similar PRE_APPEARANCE / high-risk patterns for this aisle. Safety-first decision: STOP.",
                "confidence": 0.91,
            }

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "messages": [{"role": "user", "content": prompt}],
        })

        resp = self.bedrock.invoke_model(
            modelId=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"),
            body=body,
            contentType="application/json",
            accept="application/json",
        )
        result = json.loads(resp["body"].read())
        text = result["content"][0]["text"]
        try:
            return json.loads(text)
        except Exception:
            return {"action": "ALERT", "reasoning": text, "confidence": 0.7}

    def claim_aisle_transactional(self, forklift_id: str, shadow_id: str, location: str) -> dict:
        """
        Demonstrate production-grade transactional memory.

        Uses SERIALIZABLE isolation so two concurrent agents cannot both
        claim the same aisle and silently overwrite each other’s safety decision.
        """
        conn = psycopg2.connect(self.cockroach_url)
        conn.set_isolation_level(ISOLATION_LEVEL_SERIALIZABLE)
        try:
            with conn.cursor() as cur:
                cur.execute("BEGIN")
                cur.execute(
                    """
                    SELECT forklift_id FROM near_miss_events
                    WHERE location = %s
                      AND timestamp > now() - INTERVAL '5 seconds'
                    FOR UPDATE
                    """,
                    (location,),
                )
                existing = cur.fetchall()
                if existing:
                    conn.rollback()
                    return {
                        "success": False,
                        "reason": f"Aisle already claimed by {existing[0][0]}",
                    }

                cur.execute(
                    """
                    INSERT INTO near_miss_events (forklift_id, shadow_id, location, action_taken)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (forklift_id, shadow_id, location, "STOP"),
                )
                conn.commit()
                return {"success": True}
        except Exception as e:
            conn.rollback()
            return {"success": False, "reason": str(e)}
        finally:
            conn.close()


if __name__ == "__main__":
    agent = ShadowMemoryAgent()

    current = {
        "sun_azimuth": 135.0,
        "sun_elevation": 35.0,
        "shadow_length_px": 125.0,
        "aisle_id": "aisle_3",
    }

    # Placeholder embedding for local demo (in production this comes from Bedrock Titan)
    mock_embedding = [0.1] * 1024

    print("Querying CockroachDB memory (Distributed Vector Indexing)...")
    memories = agent.query_similar_memories(mock_embedding)
    print(f"Retrieved {len(memories)} similar memories")

    decision = agent.reason(memories, current)
    print("Agent decision:", json.dumps(decision, indent=2))

    print("\nTesting SERIALIZABLE aisle claim...")
    result = agent.claim_aisle_transactional("forklift_1", "00000000-0000-0000-0000-000000000001", "aisle_3")
    print(result)
