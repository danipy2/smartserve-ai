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

ALLOWED_EXTENSIONS = [".pdf", ".txt", ".docx"]

# --- Sidebar ---
with st.sidebar:
    st.title("📄 Knowledge Base")
    st.divider()
    stats = get_collection_stats()
    st.metric("Total Documents", stats["total_documents"])
    st.metric("Total Chunks", stats["total_chunks"])
    st.divider()

    # Danger zone
    with st.expander("🗑️ Danger Zone"):
        st.caption("This will delete ALL documents from the knowledge base.")
        if st.button("Clear Entire Knowledge Base", type="secondary"):
            clear_collection()
            # Clear all document records
            for doc in get_all_documents():
                delete_document_record(doc["filename"])
                file_path = config.UPLOADS_DIR / doc["filename"]
                file_path.unlink(missing_ok=True)
            st.success("Knowledge base cleared!")
            st.rerun()

# --- Main Content ---
st.title("📄 Knowledge Base Management")
st.caption("Upload and manage your company documents, FAQs, and manuals")

# --- Upload Section ---
st.markdown("### Upload Documents")
st.markdown(
    "Upload PDF, TXT, or DOCX files. They will be automatically processed, "
    "chunked, and added to the AI's knowledge base."
)

uploaded_files = st.file_uploader(
    "Choose files to upload",
    type=["pdf", "txt", "docx"],
    accept_multiple_files=True,
    help="Supported formats: PDF, TXT, DOCX",
)

if uploaded_files:
    if st.button("📤 Process & Upload", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Processing {uploaded_file.name}...")

            # Save file to uploads directory
            file_path = config.UPLOADS_DIR / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                # Process: load, chunk, embed
                chunks = process_document(str(file_path))
                chunk_count = add_documents(chunks)

                # Record in database
                add_document_record(
                    filename=uploaded_file.name,
                    file_type=Path(uploaded_file.name).suffix.lower(),
                    chunk_count=chunk_count,
                )

                st.success(
                    f"✅ **{uploaded_file.name}** — "
                    f"{chunk_count} chunks created and embedded"
                )

            except Exception as e:
                st.error(f"❌ **{uploaded_file.name}** — Error: {str(e)}")
                file_path.unlink(missing_ok=True)

            progress_bar.progress((i + 1) / len(uploaded_files))

        status_text.text("All files processed!")
        st.rerun()

st.divider()

# --- Document List ---
st.markdown("### Uploaded Documents")

documents = get_all_documents()

if not documents:
    st.info(
        "📭 No documents uploaded yet. "
        "Upload your first document above to get started!"
    )
else:
    for doc in documents:
        col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 2, 1])

        with col1:
            # File icon based on type
            icons = {".pdf": "📕", ".txt": "📝", ".docx": "📘"}
            icon = icons.get(doc["file_type"], "📄")
            st.markdown(f"{icon} **{doc['filename']}**")

        with col2:
            st.caption(f"{doc['chunk_count']} chunks")

        with col3:
            st.caption(doc["file_type"].upper())

        with col4:
            st.caption(f"📅 {doc['uploaded_at'][:10]}")

        with col5:
            if st.button("🗑️", key=f"del_{doc['id']}", help=f"Delete {doc['filename']}"):
                # Delete from vector store
                delete_document_by_source(doc["filename"])
                # Delete database record
                delete_document_record(doc["filename"])
                # Delete file
                file_path = config.UPLOADS_DIR / doc["filename"]
                file_path.unlink(missing_ok=True)
                st.success(f"Deleted {doc['filename']}")
                st.rerun()

    st.divider()
    st.caption(f"Total: {len(documents)} documents")
