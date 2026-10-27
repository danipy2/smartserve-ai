"""
SmartServe AI — Analytics Dashboard Page
View performance metrics, conversation stats, and improvement opportunities.
"""

import streamlit as st
from pathlib import Path

# Must be first Streamlit command
st.set_page_config(
    page_title="Analytics — SmartServe AI", page_icon="📊", layout="wide"
)

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import get_analytics, init_db
import config

init_db()

# --- Main Content ---
st.title("📊 Analytics Dashboard")
st.caption("Monitor AI performance, conversation metrics, and identify improvement areas")

# Get analytics data
analytics = get_analytics()

# --- Key Metrics Row ---
st.markdown("### Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="💬 Conversations",
        value=analytics["total_conversations"],
    )

with col2:
    st.metric(
        label="📨 Total Messages",
        value=analytics["total_messages"],
    )

with col3:
    avg_conf = analytics["average_confidence"]
    st.metric(
        label="🎯 Avg Confidence",
        value=f"{avg_conf:.0%}" if avg_conf else "N/A",
    )

with col4:
    st.metric(
        label="🚨 Escalations",
        value=analytics["escalation_count"],
    )

with col5:
    st.metric(
        label="📄 Documents",
        value=analytics["total_documents"],
    )

st.divider()

# --- Charts Row ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 📈 Daily Message Volume")
    daily = analytics["daily_messages"]
    if daily:
        import pandas as pd
        df = pd.DataFrame(daily)
        df["date"] = pd.to_datetime(df["date"])
        st.bar_chart(df.set_index("date")["count"])
    else:
        st.info("No message data yet. Start chatting to see trends!")

with col_right:
    st.markdown("### 🎯 Confidence Distribution")
    if analytics["total_messages"] > 0:
        # Create a simple confidence overview
        escalation_rate = (
            analytics["escalation_count"] / max(analytics["total_messages"], 1) * 100
        )

        st.markdown(f"""
        | Metric | Value |
        |--------|-------|
        | Average Confidence | **{analytics['average_confidence']:.0%}** |
        | Escalation Rate | **{escalation_rate:.1f}%** |
        | Total Escalations | **{analytics['escalation_count']}** |
        | Confidence Threshold | **{config.CONFIDENCE_THRESHOLD:.0%}** |
        """)

        # Visual confidence bar
        st.markdown("**Confidence Level**")
        st.progress(min(analytics["average_confidence"], 1.0))
    else:
        st.info("No confidence data yet.")

st.divider()

# --- Low Confidence Queries (Improvement Opportunities) ---
st.markdown("### 🔍 Improvement Opportunities")
st.caption(
    "Questions that received low confidence scores — "
    "consider adding more relevant documents to your knowledge base."
)

low_conf = analytics["low_confidence_queries"]
if low_conf:
    for i, query_info in enumerate(low_conf, 1):
        with st.expander(
            f"❓ {query_info['question'][:80]}... "
            f"(Confidence: {query_info['confidence']:.0%})"
        ):
            st.markdown(f"**Question:** {query_info['question']}")
            st.markdown(f"**Confidence:** {query_info['confidence']:.0%}")
            st.markdown(f"**Date:** {query_info['date']}")
            st.info(
                "💡 **Tip:** Upload a document that covers this topic "
                "to improve the AI's ability to answer similar questions."
            )
else:
    st.success(
        "✅ No low-confidence queries found. "
        "The AI is performing well with the current knowledge base!"
    )

st.divider()

# --- System Health ---
st.markdown("### ⚙️ System Status")
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    | Component | Status |
    |-----------|--------|
    | LLM Model | `{config.LLM_MODEL}` |
    | Embedding Model | `{config.EMBEDDING_MODEL}` |
    | Confidence Threshold | `{config.CONFIDENCE_THRESHOLD}` |
    | Chunk Size | `{config.CHUNK_SIZE}` |
    | Chunk Overlap | `{config.CHUNK_OVERLAP}` |
    | Top K Results | `{config.TOP_K_RESULTS}` |
    """)

with col2:
    st.markdown("""
    | Component | Status |
    |-----------|--------|
    | Vector Store | 🟢 ChromaDB |
    | Database | 🟢 SQLite |
    | LLM Provider | 🟢 Google Gemini |
    | RAG Pipeline | 🟢 Active |
    """)
