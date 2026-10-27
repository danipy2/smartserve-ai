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
from core.vector_store import get_collection_stats, add_documents
from core.document_processor import process_document
from database.db import (
    get_or_create_conversation,
    add_message,
    get_chat_history,
    add_document_record,
    get_all_documents,
    init_db,
)
import config

init_db()

# ── Auto-seed sample KB if empty (so demo always works) ───────────────────────
def seed_sample_kb():
    """Load sample knowledge base on first run so the chat always has docs."""
    sample_file = config.BASE_DIR / "uploads" / "sample_knowledge_base.txt"
    if not sample_file.exists():
        return
    existing_docs = get_all_documents()
    already_seeded = any(d["filename"] == "sample_knowledge_base.txt" for d in existing_docs)
    if already_seeded:
        return
    try:
        chunks = process_document(str(sample_file))
        add_documents(chunks)
        add_document_record(
            filename="sample_knowledge_base.txt",
            file_type=".txt",
            chunk_count=len(chunks),
        )
    except Exception:
        pass  # Silent — don't crash if seeding fails

seed_sample_kb()


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

# ── Global Styles ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  #MainMenu, footer { visibility: hidden; }

  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #164e63 100%);
  }
  section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
  section[data-testid="stSidebar"] .stButton > button {
    background: rgba(14,165,233,0.2) !important;
    border: 1px solid rgba(14,165,233,0.4) !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
  }
  section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(14,165,233,0.35) !important;
  }

  .page-header {
    background: linear-gradient(135deg, #0c4a6e 0%, #0369a1 60%, #0ea5e9 100%);
    border-radius: 16px; padding: 1.6rem 2rem;
    color: white; margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 1rem;
  }
  .page-header .icon { font-size: 2.5rem; }
  .page-header h1 { font-size: 1.8rem; font-weight: 800; margin: 0 0 0.2rem; }
  .page-header p  { margin: 0; opacity: 0.85; font-size: 0.95rem; }

  .kb-status-ok {
    background: linear-gradient(135deg, #064e3b, #065f46);
    border: 1px solid #34d399;
    border-radius: 12px; padding: 1rem 1.2rem;
    color: #d1fae5; margin-bottom: 1rem;
  }
  .kb-status-warn {
    background: linear-gradient(135deg, #422006, #78350f);
    border: 1px solid #f59e0b;
    border-radius: 12px; padding: 1rem 1.2rem;
    color: #fef3c7; margin-bottom: 1rem;
  }
  .kb-status-ok h4, .kb-status-warn h4 { margin: 0 0 0.3rem; font-size: 0.9rem; font-weight: 700; }
  .kb-status-ok p, .kb-status-warn p   { margin: 0; font-size: 0.82rem; opacity: 0.9; }

  .conf-badge-high   { background:#dcfce7; color:#166534; border-radius:6px; padding:2px 10px; font-size:0.78rem; font-weight:700; }
  .conf-badge-medium { background:#fef9c3; color:#854d0e; border-radius:6px; padding:2px 10px; font-size:0.78rem; font-weight:700; }
  .conf-badge-low    { background:#fee2e2; color:#991b1b; border-radius:6px; padding:2px 10px; font-size:0.78rem; font-weight:700; }

  .source-card {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 8px; padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
  }
  .source-card strong { color: #0c4a6e; font-size: 0.88rem; }
  .source-card p { margin: 0.25rem 0 0; color: #64748b; font-size: 0.82rem; }

  .session-chip {
    background: rgba(14,165,233,0.15);
    border: 1px solid rgba(14,165,233,0.3);
    color: #7dd3fc !important;
    border-radius: 6px; padding: 3px 10px;
    font-size: 0.78rem; font-family: monospace;
    display: inline-block; margin-top: 0.5rem;
  }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🧠 SmartServe AI")
    st.markdown("*RAG Support Platform*")
    st.markdown("---")
    st.markdown("### 🗂 Navigation")
    st.markdown("""
    - 🏠 **Overview** — Home
    - 💬 **Chat** — You are here
    - 📄 **Knowledge Base** — Manage docs
    - 📊 **Analytics** — Performance
    """)
    st.markdown("---")

    # Knowledge base status
    stats = get_collection_stats()
    if stats["total_chunks"] > 0:
        st.markdown(f"""
        <div class="kb-status-ok">
          <h4>📚 Knowledge Base Active</h4>
          <p>{stats['total_documents']} document(s) &nbsp;·&nbsp; {stats['total_chunks']} chunks indexed</p>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("📑 Loaded Documents"):
            for source in stats["sources"]:
                st.markdown(f"📄 {source}")
    else:
        st.markdown("""
        <div class="kb-status-warn">
          <h4>⚠️ No Documents Loaded</h4>
          <p>Go to Knowledge Base to upload files first.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.conversation_id = get_or_create_conversation(
            st.session_state.session_id
        )
        st.rerun()

    st.markdown(
        f'<div class="session-chip">Session: {st.session_state.session_id[:8]}…</div>',
        unsafe_allow_html=True
    )

# --- Page Header ---
st.markdown("""
<div class="page-header">
  <div class="icon">💬</div>
  <div>
    <h1>AI Support Chat</h1>
    <p>Ask questions about your uploaded documents — answers include sources & confidence scores</p>
  </div>
</div>
""", unsafe_allow_html=True)

# --- Refresh stats (after sidebar) ---
stats = get_collection_stats()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show confidence and sources for assistant messages
        if message["role"] == "assistant" and "metadata" in message:
            meta = message["metadata"]
            confidence = meta.get("confidence", 0)

            # Confidence badge
            if confidence >= 0.7:
                badge_cls, label = "conf-badge-high", f"🟢 High Confidence — {confidence:.0%}"
            elif confidence >= config.CONFIDENCE_THRESHOLD:
                badge_cls, label = "conf-badge-medium", f"🟡 Medium Confidence — {confidence:.0%}"
            else:
                badge_cls, label = "conf-badge-low", f"🔴 Low Confidence — {confidence:.0%}"

            st.markdown(f'<span class="{badge_cls}">{label}</span>', unsafe_allow_html=True)

            if meta.get("needs_escalation"):
                st.warning("⚠️ Low confidence — a human agent should verify this response.")

            sources = meta.get("sources", [])
            if sources:
                with st.expander("📎 Source Citations"):
                    for src in sources:
                        st.markdown(f"""
                        <div class="source-card">
                          <strong>📄 {src['document']}</strong> &nbsp; <em>Section {src['chunk_index']}</em>
                          <p>{src['preview']}</p>
                        </div>""", unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask a question about your documents…"):
    if stats["total_chunks"] == 0:
        st.warning("⚠️ Please upload documents to the Knowledge Base first before asking questions.")
        st.stop()

    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching knowledge base and generating response…"):
            history = get_chat_history(st.session_state.conversation_id)

            add_message(
                conversation_id=st.session_state.conversation_id,
                role="user",
                content=prompt,
            )

            result = run_async(query(
                question=prompt,
                chat_history=history,
            ))

            answer = result["answer"]
            confidence = result["confidence"]
            needs_escalation = result["needs_escalation"]
            sources = result["sources"]

            add_message(
                conversation_id=st.session_state.conversation_id,
                role="assistant",
                content=answer,
                confidence=confidence,
                needs_escalation=needs_escalation,
                sources=sources,
            )

            st.markdown(answer)

            # Confidence badge
            if confidence >= 0.7:
                badge_cls, label = "conf-badge-high", f"🟢 High Confidence — {confidence:.0%}"
            elif confidence >= config.CONFIDENCE_THRESHOLD:
                badge_cls, label = "conf-badge-medium", f"🟡 Medium Confidence — {confidence:.0%}"
            else:
                badge_cls, label = "conf-badge-low", f"🔴 Low Confidence — {confidence:.0%}"

            st.markdown(f'<span class="{badge_cls}">{label}</span>', unsafe_allow_html=True)

            if needs_escalation:
                st.warning("⚠️ Low confidence — a human agent should verify this response.")

            if sources:
                with st.expander("📎 Source Citations"):
                    for src in sources:
                        st.markdown(f"""
                        <div class="source-card">
                          <strong>📄 {src['document']}</strong> &nbsp; <em>Section {src['chunk_index']}</em>
                          <p>{src['preview']}</p>
                        </div>""", unsafe_allow_html=True)

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
