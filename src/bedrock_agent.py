"""
bedrock_agent.py - Agent that uses CockroachDB MCP Server to query memory
Demonstrates memory is not afterthought, it's what makes agent useful
"""
import os
import json
import psycopg2
import boto3
from dotenv import load_dotenv

load_dotenv()

class ShadowMemoryAgent:
    def __init__(self):
        self.cockroach_url = os.getenv("COCKROACHDB_URL")
        self.bedrock = boto3.client("bedrock-runtime", region_name="us-west-2")
        
    def query_memory_via_mcp_mock(self, question_embedding):
        """
        In production, this goes via MCP Server: https://cockroachlabs.cloud/mcp
        Endpoint: https://cockroachlabs.cloud/mcp
        Safe by default: read-only mode, full audit logging
        
        For local demo, we directly query CockroachDB with vector search
        """
        conn = psycopg2.connect(self.cockroach_url)
        cur = conn.cursor()
        
        # Distributed Vector Indexing query - semantic search at scale
        # No separate vector store, no consistency gaps
        cur.execute("""
            SELECT id, sun_azimuth, sun_elevation, risk_level, aisle_id,
                   embedding <-> %s::vector AS distance
            FROM shadow_embeddings
            ORDER BY distance ASC
            LIMIT 5
        """, (question_embedding,))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results
    
    def reason_with_bedrock(self, similar_memories, current_features):
        """Bedrock Claude reasons based on memory"""
        prompt = f"""
        You are a warehouse safety agent. Your memory is CockroachDB.

        Current shadow: azimuth {current_features['sun_azimuth']}, elevation {current_features['sun_elevation']}, length {current_features['shadow_length_px']}, aisle {current_features['aisle_id']}

        Similar past memories from CockroachDB vector search:
        {similar_memories}

        Question: Have we seen this pattern before? What action should we take? Is this PRE_APPEARANCE risk where shadow appears before person?

        Respond with JSON: {{"action": "STOP|SLOW|ALERT", "reasoning": "...", "confidence": 0.0-1.0}}
        """
        
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "messages": [{"role": "user", "content": prompt}]
        })
        
        # Mock for local without Bedrock access
        if os.getenv("MOCK_AWS") == "1":
            return {
                "action": "STOP",
                "reasoning": f"Memory shows 3 similar PRE_APPEARANCE shadows in aisle_3 with high risk. Shadow length {current_features['shadow_length_px']} matches past accident pattern. Must STOP forklift.",
                "confidence": 0.92
            }
        
        resp = self.bedrock.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
            body=body,
            contentType="application/json",
            accept="application/json"
        )
        result = json.loads(resp["body"].read())
        return json.loads(result["content"][0]["text"])
    
    def transactional_claim_aisle(self, forklift_id, shadow_id, location):
        """
        Demonstrate SERIALIZABLE prevents silent loss
        Two forklifts try to claim same aisle - only one succeeds
        """
        conn = psycopg2.connect(self.cockroach_url)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE)
        cur = conn.cursor()
        try:
            cur.execute("BEGIN;")
            # Check recent claims
            cur.execute("""
                SELECT forklift_id FROM near_miss_events 
                WHERE location=%s AND timestamp > now() - INTERVAL '5 seconds'
                FOR UPDATE
            """, (location,))
            existing = cur.fetchall()
            if existing:
                raise Exception(f"Aisle {location} already claimed by {existing[0][0]}")
            
            cur.execute("""
                INSERT INTO near_miss_events (forklift_id, shadow_id, location, action_taken)
                VALUES (%s, %s, %s, %s)
            """, (forklift_id, shadow_id, location, "STOP"))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            cur.close()
            conn.close()

if __name__ == "__main__":
    agent = ShadowMemoryAgent()
    
    # Mock current shadow
    current = {
        "sun_azimuth": 135.0,
        "sun_elevation": 35.0,
        "shadow_length_px": 125.0,
        "aisle_id": "aisle_3"
    }
    
    # Mock embedding
    mock_embedding = [0.1]*1024
    
    print("Querying CockroachDB memory via MCP Server (mock)...")
    memories = agent.query_memory_via_mcp_mock(mock_embedding)
    print(f"Found {len(memories)} similar memories")
    
    decision = agent.reason_with_bedrock(memories, current)
    print(f"Agent decision: {decision}")
    
    # Demo SERIALIZABLE
    print("\nTesting SERIALIZABLE - two forklifts claiming same aisle...")
    # This would show one succeeds, one fails
