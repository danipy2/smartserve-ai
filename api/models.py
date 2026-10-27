"""
SmartServe AI — API Models
Pydantic models for request/response validation.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime


# --- Chat Models ---

class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    question: str = Field(..., min_length=1, description="The user's question")
    session_id: str = Field(..., description="Unique session identifier")


class SourceInfo(BaseModel):
    """Source document citation."""
    document: str
    chunk_index: int
    preview: str


class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""
    answer: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    needs_escalation: bool
    sources: List[SourceInfo]
    session_id: str


# --- Document Models ---

class DocumentInfo(BaseModel):
    """Information about an uploaded document."""
    id: int
    filename: str
    file_type: str
    chunk_count: int
    uploaded_at: str
    status: str


class DocumentListResponse(BaseModel):
    """Response model for listing documents."""
    documents: List[DocumentInfo]
    total_count: int


class DocumentDeleteRequest(BaseModel):
    """Request model for deleting a document."""
    filename: str


class UploadResponse(BaseModel):
    """Response model for document upload."""
    filename: str
    chunk_count: int
    message: str


# --- Analytics Models ---

class DailyMessageCount(BaseModel):
    """Daily message count for analytics."""
    date: str
    count: int


class LowConfidenceQuery(BaseModel):
    """A query that received low confidence score."""
    question: str
    confidence: float
    date: str


class AnalyticsResponse(BaseModel):
    """Response model for analytics endpoint."""
    total_conversations: int
    total_messages: int
    average_confidence: float
    escalation_count: int
    total_documents: int
    daily_messages: List[DailyMessageCount]
    low_confidence_queries: List[LowConfidenceQuery]


# --- Health Check ---

class HealthResponse(BaseModel):
    """API health check response."""
    status: str
    version: str
    timestamp: str
