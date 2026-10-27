"""
SmartServe AI — Chat Page
Interactive chat interface for customer support conversations.
"""

import asyncio
import uuid

import streamlit as st

st.set_page_config(page_title="Chat — SmartServe AI", page_icon="💬", layout="wide")

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


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# --- Session State ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = get_or_create_conversation(
        st.session_state.session_id
    )
if "kb_seeded" not in st.session_state:
    st.session_state.kb_seeded = False

# ── Styles ─────────────────────────────────────────────────────────────────────
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
    text-align: left !important;
    font-size: 0.83rem !important;
    margin-bottom: 3px !important;
  }
  section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(14,165,233,0.35) !important;
  }

  .page-header {
    background: linear-gradient(135deg, #0c4a6e 0%, #0369a1 60%, #0ea5e9 100%);
    border-radius: 16px; padding: 1.6rem 2rem;
    color: white; margin-bottom: 1.2rem;
    display: flex; align-items: center; gap: 1rem;
  }
  .page-header .icon { font-size: 2.5rem; }
  .page-header h1 { font-size: 1.8rem; font-weight: 800; margin: 0 0 0.2rem; }
  .page-header p  { margin: 0; opacity: 0.85; font-size: 0.95rem; }

  .demo-banner {
    background: linear-gradient(135deg, #064e3b, #065f46);
    border: 1px solid #34d399;
    border-radius: 14px; padding: 1.2rem 1.5rem;
    margin-bottom: 1.2rem;
    display: flex; align-items: flex-start; gap: 1rem;
  }
  .demo-banner .demo-icon { font-size: 2rem; flex-shrink: 0; }
  .demo-banner h4 { color: #6ee7b7; font-size: 1rem; font-weight: 700; margin: 0 0 0.3rem; }
  .demo-banner p  { color: #a7f3d0; font-size: 0.85rem; margin: 0; line-height: 1.6; }

  .kb-status-ok {
    background: linear-gradient(135deg, #064e3b, #065f46);
    border: 1px solid #34d399; border-radius: 12px;
    padding: 1rem 1.2rem; color: #d1fae5; margin-bottom: 1rem;
  }
  .kb-status-ok h4 { margin: 0 0 0.3rem; font-size: 0.9rem; font-weight: 700; }
  .kb-status-ok p  { margin: 0; font-size: 0.82rem; opacity: 0.9; }

  .conf-badge-high   { background:#dcfce7; color:#166534; border-radius:6px; padding:2px 10px; font-size:0.78rem; font-weight:700; }
  .conf-badge-medium { background:#fef9c3; color:#854d0e; border-radius:6px; padding:2px 10px; font-size:0.78rem; font-weight:700; }
  .conf-badge-low    { background:#fee2e2; color:#991b1b; border-radius:6px; padding:2px 10px; font-size:0.78rem; font-weight:700; }

  .source-card {
    background: #f0f9ff; border: 1px solid #bae6fd;
    border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;
  }
  .source-card strong { color: #0c4a6e; font-size: 0.88rem; }
  .source-card p { margin: 0.25rem 0 0; color: #64748b; font-size: 0.82rem; }

  .session-chip {
    background: rgba(14,165,233,0.15);
    border: 1px solid rgba(14,165,233,0.3);
    color: #7dd3fc !important; border-radius: 6px;
    padding: 3px 10px; font-size: 0.78rem; font-family: monospace;
    display: inline-block; margin-top: 0.5rem;
  }
  .demo-q-label {
    color: #7dd3fc !important; font-size: 0.78rem !important;
    font-weight: 600 !important; text-transform: uppercase;
    letter-spacing: 0.05em; margin-bottom: 6px !important; display: block;
  }
</style>
""", unsafe_allow_html=True)

# ── Page Header (render early so page doesn't look blank during seeding) ───────
st.markdown("""
<div class="page-header">
  <div class="icon">💬</div>
  <div>
    <h1>AI Support Chat</h1>
    <p>Answers come with source citations & confidence scores — powered by Gemini RAG</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Auto-seed demo KB ──────────────────────────────────────────────────────────
# Run AFTER page header so user sees something while it loads
stats = get_collection_stats()

if stats["total_chunks"] == 0 and not st.session_state.kb_seeded:
    sample_file = config.BASE_DIR / "uploads" / "sample_knowledge_base.txt"
    if sample_file.exists():
        existing_docs = get_all_documents()
        already_in_db = any(d["filename"] == "sample_knowledge_base.txt" for d in existing_docs)
        if not already_in_db:
            with st.spinner("⚙️ Loading demo knowledge base — takes ~10 seconds on first visit…"):
                try:
                    chunks = process_document(str(sample_file))
                    add_documents(chunks)
                    add_document_record(
                        filename="sample_knowledge_base.txt",
                        file_type=".txt",
                        chunk_count=len(chunks),
                    )
                    st.session_state.kb_seeded = True
                    st.rerun()  # Refresh so stats updates everywhere
                except Exception as e:
                    st.warning(f"⚠️ Could not auto-load demo document: {e}. Please upload a document in the Knowledge Base page.")
        else:
            # SQLite says seeded but ChromaDB is empty — re-embed
            with st.spinner("⚙️ Re-indexing demo knowledge base…"):
                try:
                    chunks = process_document(str(sample_file))
                    add_documents(chunks)
                    st.session_state.kb_seeded = True
                    st.rerun()
                except Exception as e:
                    st.warning(f"⚠️ Could not re-index demo document: {e}")

# Re-fetch stats after potential seeding
stats = get_collection_stats()

# ── Sidebar ────────────────────────────────────────────────────────────────────
DEMO_QUESTIONS = [
    "What is your return policy?",
    "How do I claim warranty on a laptop?",
    "What payment methods do you accept?",
    "How long does delivery to Hawassa take?",
    "Do you offer bulk discounts?",
    "What are your branch locations and hours?",
    "How do I track my order?",
]

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

    if stats["total_chunks"] > 0:
        st.markdown(f"""
        <div class="kb-status-ok">
          <h4>📚 Knowledge Base Active</h4>
          <p>{stats['total_documents']} doc(s) &nbsp;·&nbsp; {stats['total_chunks']} chunks indexed</p>
        </div>
        """, unsafe_allow_html=True)
        with st.expander("📑 Loaded Documents"):
            for source in stats["sources"]:
                label = "🔖 Demo" if source == "sample_knowledge_base.txt" else "📄"
                st.markdown(f"{label} {source}")
    else:
        st.info("⏳ Knowledge base loading…")

    st.markdown("---")
    st.markdown('<span class="demo-q-label">💡 Click to ask</span>', unsafe_allow_html=True)
    for q in DEMO_QUESTIONS:
        if st.button(q, key=f"dq_{q[:25]}", use_container_width=True):
            st.session_state.pending_question = q
            st.rerun()

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

# ── Demo Banner ────────────────────────────────────────────────────────────────
if stats["total_chunks"] > 0:
    st.markdown("""
    <div class="demo-banner">
      <div class="demo-icon">🚀</div>
      <div>
        <h4>Demo Document Pre-loaded — Start Chatting Now!</h4>
        <p>
          We've loaded a <strong>BizCorp Ethiopia Customer Support Knowledge Base</strong>
          covering return policies, warranties, delivery, payments, branches & FAQs.<br>
          <em>👈 Click any question in the sidebar, or type your own below.
          Want to test with your own file? Go to 📄 Knowledge Base to upload a PDF, DOCX, or TXT.</em>
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Chat History ───────────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant" and "metadata" in message:
            meta = message["metadata"]
            confidence = meta.get("confidence", 0)

            if confidence >= 0.7:
                badge_cls, label = "conf-badge-high",   f"🟢 High Confidence — {confidence:.0%}"
            elif confidence >= config.CONFIDENCE_THRESHOLD:
                badge_cls, label = "conf-badge-medium", f"🟡 Medium Confidence — {confidence:.0%}"
            else:
                badge_cls, label = "conf-badge-low",    f"🔴 Low Confidence — {confidence:.0%}"

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

# ── Chat Input ─────────────────────────────────────────────────────────────────
pending = st.session_state.pop("pending_question", None)
prompt  = st.chat_input("Ask anything about the knowledge base…")
if pending and not prompt:
    prompt = pending

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching knowledge base…"):
            history = get_chat_history(st.session_state.conversation_id)

            add_message(
                conversation_id=st.session_state.conversation_id,
                role="user",
                content=prompt,
            )

            result = run_async(query(question=prompt, chat_history=history))

            answer           = result["answer"]
            confidence       = result["confidence"]
            needs_escalation = result["needs_escalation"]
            sources          = result["sources"]

            add_message(
                conversation_id=st.session_state.conversation_id,
                role="assistant",
                content=answer,
                confidence=confidence,
                needs_escalation=needs_escalation,
                sources=sources,
            )

            st.markdown(answer)

            if confidence >= 0.7:
                badge_cls, label = "conf-badge-high",   f"🟢 High Confidence — {confidence:.0%}"
            elif confidence >= config.CONFIDENCE_THRESHOLD:
                badge_cls, label = "conf-badge-medium", f"🟡 Medium Confidence — {confidence:.0%}"
            else:
                badge_cls, label = "conf-badge-low",    f"🔴 Low Confidence — {confidence:.0%}"

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

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "metadata": {
            "confidence": confidence,
            "needs_escalation": needs_escalation,
            "sources": sources,
        },
    })
