"""
SmartServe AI — Document Processor
Handles loading, chunking, and processing of uploaded documents (PDF, TXT, DOCX).
"""

from pathlib import Path
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from pypdf import PdfReader

import config


def load_pdf(file_path: str) -> str:
    """Extract text content from a PDF file."""
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def load_txt(file_path: str) -> str:
    """Load text content from a plain text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_docx(file_path: str) -> str:
    """Extract text content from a DOCX file."""
    from docx import Document as DocxDocument
    doc = DocxDocument(file_path)
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text.strip()


def load_document(file_path: str) -> str:
    """
    Load a document and extract its text content.
    Supports PDF, TXT, and DOCX formats.
    """
    path = Path(file_path)
    extension = path.suffix.lower()

    loaders = {
        ".pdf": load_pdf,
        ".txt": load_txt,
        ".docx": load_docx,
    }

    loader = loaders.get(extension)
    if loader is None:
        raise ValueError(
            f"Unsupported file format: {extension}. "
            f"Supported formats: {', '.join(loaders.keys())}"
        )

    return loader(file_path)


def chunk_document(
    text: str,
    source: str,
    chunk_size: int = config.CHUNK_SIZE,
    chunk_overlap: int = config.CHUNK_OVERLAP,
) -> List[Document]:
    """
    Split document text into overlapping chunks for embedding.

    Args:
        text: The full document text.
        source: The source filename (stored as metadata).
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between consecutive chunks.

    Returns:
        List of LangChain Document objects with metadata.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.create_documents(
        texts=[text],
        metadatas=[{"source": source}],
    )

    # Add chunk index to metadata for source citation
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
        chunk.metadata["total_chunks"] = len(chunks)

    return chunks


def process_document(file_path: str) -> List[Document]:
    """
    Full pipeline: load a document and split it into chunks.

    Args:
        file_path: Path to the document file.

    Returns:
        List of chunked Document objects ready for embedding.
    """
    source = Path(file_path).name
    text = load_document(file_path)

    if not text:
        raise ValueError(f"No text content found in {source}")

    chunks = chunk_document(text, source)
    return chunks
