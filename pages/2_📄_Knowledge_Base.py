"""
SmartServe AI — Knowledge Base Management Page
Upload, view, and manage documents in the knowledge base.
"""

import streamlit as st
import shutil
from pathlib import Path

# Must be first Streamlit command
st.set_page_config(
    page_title="Knowledge Base — SmartServe AI", page_icon="📄", layout="wide"
)

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.document_processor import process_document
from core.vector_store import (
    add_documents,
    delete_document_by_source,
    get_collection_stats,
    clear_collection,
)
from database.db import (
    add_document_record,
    get_all_documents,
    delete_document_record,
    init_db,
)
import config

init_db()

# ── Auto-seed sample KB if empty ──────────────────────────────────────────────
def seed_sample_kb():
    """Load sample knowledge base on first run so the demo always has documents."""
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
        pass

seed_sample_kb()

ALLOWED_EXTENSIONS = [".pdf", ".txt", ".docx"]

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

  .page-header {
    background: linear-gradient(135deg, #0c4a6e 0%, #0369a1 60%, #0ea5e9 100%);
    border-radius: 16px; padding: 1.6rem 2rem;
    color: white; margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 1rem;
  }
  .page-header .icon { font-size: 2.5rem; }
  .page-header h1 { font-size: 1.8rem; font-weight: 800; margin: 0 0 0.2rem; }
  .page-header p  { margin: 0; opacity: 0.85; font-size: 0.95rem; }

  .stat-card {
    background: linear-gradient(135deg, #0c4a6e, #0369a1);
    border-radius: 14px; padding: 1.2rem 1.5rem;
    color: white; text-align: center;
  }
  .stat-card .val { font-size: 2.2rem; font-weight: 800; }
  .stat-card .lbl { font-size: 0.82rem; opacity: 0.85; margin-top: 0.2rem; }

  .section-title {
    font-size: 1.15rem; font-weight: 700;
    color: #0c4a6e; border-left: 4px solid #0ea5e9;
    padding-left: 0.8rem; margin: 2rem 0 1rem;
  }

  .upload-zone {
    background: #f0f9ff;
    border: 2px dashed #7dd3fc;
    border-radius: 14px; padding: 1.5rem;
    margin-bottom: 1rem;
  }

  .doc-row {
    background: white;
    border: 1px solid #e0f2fe;
    border-left: 4px solid #0ea5e9;
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.6rem;
    display: flex; align-items: center;
    box-shadow: 0 2px 8px rgba(14,165,233,0.06);
  }
  .doc-icon  { font-size: 1.6rem; margin-right: 1rem; }
  .doc-name  { font-weight: 700; color: #0c4a6e; font-size: 0.95rem; }
  .doc-meta  { color: #64748b; font-size: 0.82rem; margin-top: 0.15rem; }

  .danger-zone {
    background: #1c0a0a;
    border: 1px solid #7f1d1d;
    border-radius: 12px; padding: 1.2rem 1.5rem;
    margin-top: 1rem;
  }
  .danger-zone h4 { color: #fca5a5; margin: 0 0 0.5rem; font-size: 0.95rem; }
  .danger-zone p  { color: #fca5a5; font-size: 0.82rem; margin: 0 0 0.8rem; opacity: 0.8; }
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
    - 💬 **Chat** — Talk to the AI
    - 📄 **Knowledge Base** — You are here
    - 📊 **Analytics** — Performance
    """)
    st.markdown("---")

    stats = get_collection_stats()
    st.markdown("### 📊 Quick Stats")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""
        <div class="stat-card">
          <div class="val">{stats['total_documents']}</div>
          <div class="lbl">Documents</div>
        </div>""", unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div class="stat-card">
          <div class="val">{stats['total_chunks']}</div>
          <div class="lbl">Chunks</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="danger-zone">
      <h4>🗑️ Danger Zone</h4>
      <p>Permanently deletes ALL documents from the knowledge base.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Clear Entire Knowledge Base", type="secondary", use_container_width=True):
        clear_collection()
        for doc in get_all_documents():
            delete_document_record(doc["filename"])
            file_path = config.UPLOADS_DIR / doc["filename"]
            file_path.unlink(missing_ok=True)
        st.success("Knowledge base cleared!")
        st.rerun()

# --- Page Header ---
st.markdown("""
<div class="page-header">
  <div class="icon">📄</div>
  <div>
    <h1>Knowledge Base</h1>
    <p>Upload PDFs, Word docs, and text files — they're automatically chunked, embedded, and indexed for AI retrieval</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stats Row ──────────────────────────────────────────────────────────────────
stats = get_collection_stats()
c1, c2, c3 = st.columns(3)
c1.metric("📄 Total Documents", stats["total_documents"])
c2.metric("🧩 Total Chunks", stats["total_chunks"])
c3.metric("📁 Supported Formats", "PDF · TXT · DOCX")

# ── Upload Section ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📤 Upload Documents</div>', unsafe_allow_html=True)

st.markdown("""
<div class="upload-zone">
  <p style="margin:0;color:#0369a1;font-size:0.9rem;">
    📂 Drop <strong>PDF, TXT, or DOCX</strong> files below. Each file is automatically
    split into overlapping chunks, embedded using Gemini, and stored in ChromaDB for
    semantic search.
  </p>
</div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Choose files to upload",
    type=["pdf", "txt", "docx"],
    accept_multiple_files=True,
    help="Supported formats: PDF, TXT, DOCX",
    label_visibility="collapsed",
)

if uploaded_files:
    if st.button("⚡ Process & Add to Knowledge Base", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"⚙️ Processing {uploaded_file.name}…")

            file_path = config.UPLOADS_DIR / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                chunks = process_document(str(file_path))
                chunk_count = add_documents(chunks)

                add_document_record(
                    filename=uploaded_file.name,
                    file_type=Path(uploaded_file.name).suffix.lower(),
                    chunk_count=chunk_count,
                )

                st.success(
                    f"✅ **{uploaded_file.name}** — {chunk_count} chunks created and embedded"
                )

            except Exception as e:
                st.error(f"❌ **{uploaded_file.name}** — Error: {str(e)}")
                file_path.unlink(missing_ok=True)

            progress_bar.progress((i + 1) / len(uploaded_files))

        status_text.success("✅ All files processed!")
        st.rerun()

# ── Document List ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📚 Uploaded Documents</div>', unsafe_allow_html=True)

documents = get_all_documents()

if not documents:
    st.info(
        "📭 No documents uploaded yet. "
        "Upload your first document above to get started!"
    )
else:
    FILE_ICONS = {".pdf": "📕", ".txt": "📝", ".docx": "📘"}
    for doc in documents:
        icon = FILE_ICONS.get(doc["file_type"], "📄")
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(f"""
            <div class="doc-row">
              <div class="doc-icon">{icon}</div>
              <div>
                <div class="doc-name">{doc['filename']}</div>
                <div class="doc-meta">
                  {doc['file_type'].upper()} &nbsp;·&nbsp;
                  {doc['chunk_count']} chunks &nbsp;·&nbsp;
                  Uploaded {doc['uploaded_at'][:10]}
                </div>
              </div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Delete", key=f"del_{doc['id']}", use_container_width=True):
                delete_document_by_source(doc["filename"])
                delete_document_record(doc["filename"])
                file_path = config.UPLOADS_DIR / doc["filename"]
                file_path.unlink(missing_ok=True)
                st.success(f"Deleted {doc['filename']}")
                st.rerun()

    st.caption(f"Total: {len(documents)} document(s) — {stats['total_chunks']} chunks indexed")
