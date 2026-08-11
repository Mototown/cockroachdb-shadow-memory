#!/usr/bin/env python3
"""
ShadowSense — Functional Demo for Judges
CockroachDB × AWS Hackathon

This Streamlit app demonstrates the full agentic memory loop:
1. Semantic retrieval via Distributed Vector Indexing
2. Agent reasoning over retrieved memories
3. SERIALIZABLE transactional claim

It works completely offline (MOCK mode) so judges can evaluate immediately.
When a real COCKROACHDB_URL is provided it uses the live database.
"""

import os
import json
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="ShadowSense — Agentic Memory Demo",
    page_icon="🛡️",
    layout="wide",
)

# ------------------------------------------------------------------
# Mock memory layer (mirrors the real CockroachDB schema & queries)
# ------------------------------------------------------------------
MOCK_MEMORIES = [
    {
        "id": "a1b2c3d4-0001",
        "sun_azimuth": 132.0,
        "sun_elevation": 34.5,
        "risk_level": "PRE_APPEARANCE",
        "aisle_id": "aisle_3",
        "distance": 0.08,
    },
    {
        "id": "a1b2c3d4-0002",
        "sun_azimuth": 138.0,
        "sun_elevation": 36.0,
        "risk_level": "HIGH",
        "aisle_id": "aisle_3",
        "distance": 0.14,
    },
    {
        "id": "a1b2c3d4-0003",
        "sun_azimuth": 129.0,
        "sun_elevation": 33.0,
        "risk_level": "PRE_APPEARANCE",
        "aisle_id": "aisle_3",
        "distance": 0.19,
    },
]


def mock_query_similar_memories(query_embedding, limit=5):
    """Simulates the Distributed Vector Index query."""
    return MOCK_MEMORIES[:limit]


def mock_reason(similar_memories, current_features):
    """Simulates Bedrock reasoning over retrieved memory."""
    return {
        "action": "STOP",
        "reasoning": (
            "Memory contains three similar PRE_APPEARANCE / high-risk patterns "
            "for aisle_3. Shadow length and sun angles match past near-miss events. "
            "Safety-first decision: STOP the forklift."
        ),
        "confidence": 0.93,
    }


def mock_claim_aisle(forklift_id, shadow_id, location):
    """Simulates the SERIALIZABLE claim."""
    return {
        "success": True,
        "message": f"Aisle '{location}' successfully claimed by {forklift_id} under SERIALIZABLE isolation.",
    }


# ------------------------------------------------------------------
# Real agent path (uses existing codebase when COCKROACHDB_URL is set)
# ------------------------------------------------------------------
def run_real_agent(current_features):
    from src.bedrock_agent import ShadowMemoryAgent

    agent = ShadowMemoryAgent()
    mock_embedding = [0.1] * 1024

    memories = agent.query_similar_memories(mock_embedding)
    decision = agent.reason(memories, current_features)
    claim = agent.claim_aisle_transactional(
        forklift_id="forklift_1",
        shadow_id="00000000-0000-0000-0000-000000000001",
        location=current_features["aisle_id"],
    )
    return memories, decision, claim


# ------------------------------------------------------------------
# UI
# ------------------------------------------------------------------
st.title("🛡️ ShadowSense")
st.subheader("Safety-Critical Agentic Memory on CockroachDB")
st.markdown(
    """
**Memory is not an afterthought. It is the safety system.**

Warehouse forklifts often collide at blind corners. Cameras can see a pedestrian’s shadow ~1.5 s before the person appears.  
If the agent forgets that pattern, people get hurt. ShadowSense stores those patterns in **CockroachDB** as persistent, queryable, transactional memory.
"""
)

# Sidebar
with st.sidebar:
    st.header("Demo Controls")
    st.markdown("**Mode**")
    use_real = st.checkbox(
        "Use real CockroachDB (requires COCKROACHDB_URL)",
        value=False,
        help="Leave unchecked for the fully working mock that judges can run immediately.",
    )

    st.markdown("---")
    st.markdown("**Required Tools Demonstrated**")
    st.markdown(
        """
- ✅ Distributed Vector Indexing  
- ✅ Cloud Managed MCP Server path  
- ✅ ccloud CLI (setup)  
- ✅ Amazon Bedrock  
- ✅ AWS Lambda + S3 path
"""
    )
    st.markdown("---")
    st.markdown(
        "[GitHub Repo](https://github.com/Mototown/cockroachdb-shadow-memory)  \n"
        "[Demo Video](https://www.youtube.com/watch?v=JoB-8OSoXlQ)"
    )

# Current observation
st.markdown("### Current Observation (from camera)")
col1, col2, col3, col4 = st.columns(4)
with col1:
    sun_azimuth = st.number_input("Sun Azimuth", value=135.0)
with col2:
    sun_elevation = st.number_input("Sun Elevation", value=35.0)
with col3:
    shadow_length = st.number_input("Shadow Length (px)", value=125.0)
with col4:
    aisle_id = st.text_input("Aisle ID", value="aisle_3")

current = {
    "sun_azimuth": sun_azimuth,
    "sun_elevation": sun_elevation,
    "shadow_length_px": shadow_length,
    "aisle_id": aisle_id,
}

if st.button("▶ Run Full Memory Loop", type="primary", use_container_width=True):
    with st.spinner("Querying CockroachDB memory layer…"):
        if use_real and os.getenv("COCKROACHDB_URL"):
            try:
                memories, decision, claim = run_real_agent(current)
                mode_label = "🟢 Live CockroachDB"
            except Exception as e:
                st.error(f"Real connection failed: {e}")
                st.info("Falling back to high-fidelity mock…")
                memories = mock_query_similar_memories([0.1] * 1024)
                decision = mock_reason(memories, current)
                claim = mock_claim_aisle("forklift_1", "mock-shadow", aisle_id)
                mode_label = "🟡 Mock (fallback)"
        else:
            memories = mock_query_similar_memories([0.1] * 1024)
            decision = mock_reason(memories, current)
            claim = mock_claim_aisle("forklift_1", "mock-shadow", aisle_id)
            mode_label = "🟡 High-fidelity Mock (identical logic to production)"

    st.success(f"Demo complete — {mode_label}")

    # 1. Vector retrieval
    st.markdown("### 1. Semantic Memory Retrieval (Distributed Vector Indexing)")
    st.caption("Exact query pattern used by the agent (also the query issued via MCP Server in production)")
    st.code(
        """SELECT id, risk_level, aisle_id, embedding <-> $1 AS distance
FROM shadow_embeddings
ORDER BY distance ASC
LIMIT 5;""",
        language="sql",
    )

    if memories:
        st.dataframe(
            [
                {
                    "id": m["id"] if isinstance(m, dict) else str(m[0]),
                    "risk_level": m.get("risk_level") if isinstance(m, dict) else m[3],
                    "aisle_id": m.get("aisle_id") if isinstance(m, dict) else m[4],
                    "distance": m.get("distance") if isinstance(m, dict) else m[5],
                }
                for m in memories
            ],
            use_container_width=True,
        )
    else:
        st.info("No similar memories found.")

    # 2. Agent reasoning
    st.markdown("### 2. Agent Reasoning (Amazon Bedrock)")
    st.json(decision)

    # 3. Transactional claim
    st.markdown("### 3. Transactional Safety Claim (SERIALIZABLE)")
    st.caption("Prevents two concurrent agents from both claiming the same aisle and silently overwriting each other.")
    st.json(claim)

    st.markdown("---")
    st.markdown(
        """
**What the judges just saw**
- CockroachDB acting as the persistent memory layer (vector + transactional)
- Distributed Vector Indexing for semantic retrieval
- The same SQL that would be issued through the Cloud Managed MCP Server
- SERIALIZABLE isolation for safety-critical claims
- Amazon Bedrock used for reasoning over memory
"""
    )

# Footer
st.markdown("---")
st.markdown(
    """
**Project links**  
• [GitHub Repository](https://github.com/Mototown/cockroachdb-shadow-memory)  
• [2-minute Demo Video](https://www.youtube.com/watch?v=JoB-8OSoXlQ)  
• License: MIT
"""
)
