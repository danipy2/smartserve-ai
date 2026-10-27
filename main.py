"""
SmartServe AI — FastAPI Application
Main API entry point with all routes and CORS configuration.
"""

from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.models import HealthResponse
from api.routes import chat, documents, analytics
from database.db import init_db

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="SmartServe AI",
    description=(
        "Intelligent Customer Support Agent Platform — "
        "An AI-powered system that enables businesses to create smart chatbots "
        "from their own documents using RAG (Retrieval-Augmented Generation)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(chat.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    """API root — redirect info."""
    return {
        "app": "SmartServe AI",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """API health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
