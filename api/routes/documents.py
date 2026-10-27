"""
SmartServe AI — Document Management API Routes
Endpoints for uploading, listing, and deleting knowledge base documents.
"""

import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from api.models import (
    DocumentInfo,
    DocumentListResponse,
    DocumentDeleteRequest,
    UploadResponse,
)
from core.document_processor import process_document
from core.vector_store import add_documents, delete_document_by_source
from database.db import (
    add_document_record,
    get_all_documents,
    delete_document_record,
)
import config

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document to the knowledge base.
    
    Accepts PDF, TXT, and DOCX files. The document is processed,
    chunked, embedded, and stored in the vector database.
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. "
                   f"Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Save uploaded file
    file_path = config.UPLOADS_DIR / file.filename
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Process document: load, chunk, embed
    try:
        chunks = process_document(str(file_path))
        chunk_count = add_documents(chunks)

        # Record in database
        add_document_record(
            filename=file.filename,
            file_type=file_ext,
            chunk_count=chunk_count,
        )

        return UploadResponse(
            filename=file.filename,
            chunk_count=chunk_count,
            message=f"Successfully processed {file.filename} into {chunk_count} chunks.",
        )

    except ValueError as e:
        # Clean up saved file on processing error
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")


@router.get("/", response_model=DocumentListResponse)
async def list_documents():
    """List all documents in the knowledge base."""
    documents = get_all_documents()
    doc_list = [DocumentInfo(**doc) for doc in documents]
    return DocumentListResponse(
        documents=doc_list,
        total_count=len(doc_list),
    )


@router.delete("/")
async def delete_document(request: DocumentDeleteRequest):
    """
    Remove a document from the knowledge base.
    Deletes both the vector store embeddings and the database record.
    """
    try:
        # Delete from vector store
        chunks_deleted = delete_document_by_source(request.filename)

        # Delete database record
        delete_document_record(request.filename)

        # Delete the file
        file_path = config.UPLOADS_DIR / request.filename
        file_path.unlink(missing_ok=True)

        return {
            "message": f"Deleted {request.filename} ({chunks_deleted} chunks removed)",
            "filename": request.filename,
            "chunks_deleted": chunks_deleted,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
