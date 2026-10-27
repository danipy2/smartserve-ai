"""
SmartServe AI — Chat API Routes
Endpoints for customer chat interactions.
"""

from fastapi import APIRouter, HTTPException

from api.models import ChatRequest, ChatResponse, SourceInfo
from core.rag_chain import query
from database.db import (
    get_or_create_conversation,
    add_message,
    get_chat_history,
)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get an AI-powered response.
    
    The AI retrieves relevant information from the knowledge base,
    generates a response, evaluates its confidence, and determines
    if human escalation is needed.
    """
    try:
        # Get or create conversation
        conversation_id = get_or_create_conversation(request.session_id)

        # Get chat history for context
        history = get_chat_history(conversation_id)

        # Store user message
        add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.question,
        )

        # Run RAG query
        result = await query(
            question=request.question,
            chat_history=history,
        )

        # Store assistant response
        add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=result["answer"],
            confidence=result["confidence"],
            needs_escalation=result["needs_escalation"],
            sources=result["sources"],
        )

        # Build response
        sources = [SourceInfo(**s) for s in result["sources"]]

        return ChatResponse(
            answer=result["answer"],
            confidence=result["confidence"],
            needs_escalation=result["needs_escalation"],
            sources=sources,
            session_id=request.session_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
