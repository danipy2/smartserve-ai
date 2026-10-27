"""
SmartServe AI — Vector Store Manager
Manages ChromaDB vector store for document embeddings storage and retrieval.
"""

from typing import List, Optional, Dict

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

import config


def get_embedding_function() -> GoogleGenerativeAIEmbeddings:
    """Initialize the Google Gemini embedding model."""
    return GoogleGenerativeAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        google_api_key=config.GOOGLE_API_KEY,
    )


def get_vector_store(collection_name: str = "default") -> Chroma:
    """
    Get or create a ChromaDB vector store instance.

    Args:
        collection_name: Name of the collection (enables multi-tenant support).

    Returns:
        Chroma vector store instance.
    """
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embedding_function(),
        persist_directory=str(config.CHROMA_DIR),
    )


def add_documents(
    documents: List[Document],
    collection_name: str = "default",
) -> int:
    """
    Add document chunks to the vector store.

    Args:
        documents: List of chunked Document objects to embed and store.
        collection_name: Target collection name.

    Returns:
        Number of documents added.
    """
    vector_store = get_vector_store(collection_name)
    vector_store.add_documents(documents)
    return len(documents)


def similarity_search(
    query: str,
    collection_name: str = "default",
    k: int = config.TOP_K_RESULTS,
) -> List[Document]:
    """
    Search for the most relevant document chunks for a given query.

    Args:
        query: The user's question or search query.
        collection_name: Collection to search in.
        k: Number of top results to return.

    Returns:
        List of the most relevant Document objects.
    """
    vector_store = get_vector_store(collection_name)
    results = vector_store.similarity_search(query, k=k)
    return results


def similarity_search_with_scores(
    query: str,
    collection_name: str = "default",
    k: int = config.TOP_K_RESULTS,
) -> List[tuple]:
    """
    Search with relevance scores for confidence assessment.

    Args:
        query: The user's question.
        collection_name: Collection to search in.
        k: Number of top results.

    Returns:
        List of (Document, score) tuples. Lower score = more relevant.
    """
    vector_store = get_vector_store(collection_name)
    results = vector_store.similarity_search_with_score(query, k=k)
    return results


def get_collection_stats(collection_name: str = "default") -> Dict:
    """
    Get statistics about a vector store collection.

    Returns:
        Dictionary with collection info (document count, sources, etc.).
    """
    vector_store = get_vector_store(collection_name)
    collection = vector_store._collection

    count = collection.count()
    sources = set()

    if count > 0:
        # Get all metadata to extract unique sources
        all_data = collection.get(include=["metadatas"])
        if all_data and all_data["metadatas"]:
            sources = set(
                m.get("source", "Unknown") for m in all_data["metadatas"]
            )

    return {
        "total_chunks": count,
        "total_documents": len(sources),
        "sources": list(sources),
    }


def delete_document_by_source(
    source: str,
    collection_name: str = "default",
) -> int:
    """
    Delete all chunks belonging to a specific source document.

    Args:
        source: The source filename to delete.
        collection_name: Collection to delete from.

    Returns:
        Number of chunks deleted.
    """
    vector_store = get_vector_store(collection_name)
    collection = vector_store._collection

    # Find all IDs with this source
    all_data = collection.get(include=["metadatas"])
    ids_to_delete = []

    if all_data and all_data["metadatas"]:
        for i, metadata in enumerate(all_data["metadatas"]):
            if metadata.get("source") == source:
                ids_to_delete.append(all_data["ids"][i])

    if ids_to_delete:
        collection.delete(ids=ids_to_delete)

    return len(ids_to_delete)


def clear_collection(collection_name: str = "default") -> None:
    """Delete all documents from a collection."""
    vector_store = get_vector_store(collection_name)
    collection = vector_store._collection
    all_data = collection.get()
    if all_data["ids"]:
        collection.delete(ids=all_data["ids"])
