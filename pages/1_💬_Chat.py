"""
SmartServe AI — Chat Page
Interactive chat interface for customer support conversations.
"""

import asyncio
import uuid

import streamlit as st

# Must be first Streamlit command
st.set_page_config(page_title="Chat — SmartServe AI", page_icon="💬", layout="wide")

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.rag_chain import query
from core.vector_store import get_collection_stats
from database.db import (
    get_or_create_conversation,
    add_message,
    get_chat_history,
    init_db,
)
import config

init_db()


def run_async(coro):
    """Helper to run async functions in Streamlit."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# --- Session State Initialization ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = get_or_create_conversation(
        st.session_state.session_id
    )

# --- Sidebar ---
with st.sidebar:
    st.title("💬 Chat Settings")
    st.divider()

    # Knowledge base status
    stats = get_collection_stats()
    if stats["total_chunks"] > 0:
        st.success(f"📚 Knowledge Base: {stats['total_documents']} documents ({stats['total_chunks']} chunks)")
        with st.expander("Loaded Documents"):
            for source in stats["sources"]:
                st.markdown(f"- 📄 {source}")
    else:
        st.warning("⚠️ No documents loaded. Go to Knowledge Base to upload documents first.")

    st.divider()

    # New conversation button
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.conversation_id = get_or_create_conversation(
            st.session_state.session_id
        )
        st.rerun()

    st.divider()
    st.caption(f"Session: `{st.session_state.session_id[:8]}...`")

# --- Main Chat Interface ---
st.title("💬 SmartServe AI Chat")
st.caption("Ask questions about the uploaded knowledge base documents")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show confidence and sources for assistant messages
        if message["role"] == "assistant" and "metadata" in message:
            meta = message["metadata"]
            confidence = meta.get("confidence", 0)

            # Confidence indicator
            if confidence >= 0.7:
                conf_color = "🟢"
                conf_label = "High"
            elif confidence >= config.CONFIDENCE_THRESHOLD:
                conf_color = "🟡"
                conf_label = "Medium"
            else:
                conf_color = "🔴"
                conf_label = "Low"

            col1, col2 = st.columns([1, 3])
            with col1:
                st.caption(f"{conf_color} Confidence: {confidence:.0%} ({conf_label})")

            # Escalation warning
            if meta.get("needs_escalation"):
                st.warning(
                    "⚠️ This answer has low confidence. "
                    "A human agent should verify this response."
                )

            # Source citations
            sources = meta.get("sources", [])
            if sources:
                with st.expander("📎 Sources"):
                    for src in sources:
                        st.markdown(
                            f"**{src['document']}** (Section {src['chunk_index']})"
                        )
                        st.caption(src["preview"])

# Chat input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Check if knowledge base has documents
    if stats["total_chunks"] == 0:
        st.warning(
            "⚠️ Please upload documents to the Knowledge Base first "
            "before asking questions."
        )
        st.stop()

    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base and generating response..."):
            # Get chat history
            history = get_chat_history(st.session_state.conversation_id)

            # Store user message in DB
            add_message(
                conversation_id=st.session_state.conversation_id,
                role="user",
                content=prompt,
            )

            # Run RAG query
            result = run_async(query(
                question=prompt,
                chat_history=history,
            ))

            answer = result["answer"]
            confidence = result["confidence"]
            needs_escalation = result["needs_escalation"]
            sources = result["sources"]

            # Store assistant response in DB
            add_message(
                conversation_id=st.session_state.conversation_id,
                role="assistant",
                content=answer,
                confidence=confidence,
                needs_escalation=needs_escalation,
                sources=sources,
            )

            # Display answer
            st.markdown(answer)

            # Confidence indicator
            if confidence >= 0.7:
                conf_color = "🟢"
                conf_label = "High"
            elif confidence >= config.CONFIDENCE_THRESHOLD:
                conf_color = "🟡"
                conf_label = "Medium"
            else:
                conf_color = "🔴"
                conf_label = "Low"

            col1, col2 = st.columns([1, 3])
            with col1:
                st.caption(f"{conf_color} Confidence: {confidence:.0%} ({conf_label})")

            if needs_escalation:
                st.warning(
                    "⚠️ This answer has low confidence. "
                    "A human agent should verify this response."
                )

            if sources:
                with st.expander("📎 Sources"):
                    for src in sources:
                        st.markdown(
                            f"**{src['document']}** (Section {src['chunk_index']})"
                        )
                        st.caption(src["preview"])

    # Save to session state
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "metadata": {
            "confidence": confidence,
            "needs_escalation": needs_escalation,
            "sources": sources,
        },
    })
