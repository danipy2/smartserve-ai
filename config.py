"""
SmartServe AI — Configuration
Centralised configuration for the application.
Supports both local .env and Streamlit Cloud secrets.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Load Streamlit Cloud secrets if available (Render.com uses os.environ directly) ---
try:
    import streamlit as st
    if hasattr(st, "secrets"):
        if "GOOGLE_API_KEY" in st.secrets:
            os.environ.setdefault("GOOGLE_API_KEY", st.secrets["GOOGLE_API_KEY"])
except Exception:
    pass  # Render.com: env vars already in os.environ

# --- Paths ---
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = DATA_DIR / "chroma"
UPLOADS_DIR = BASE_DIR / "uploads"
DB_PATH = DATA_DIR / "smartserve.db"

# Ensure directories exist
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# --- API Keys ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# --- Model Configuration ---
LLM_MODEL = "gemini-3.8-flash"
EMBEDDING_MODEL = "models/text-embedding-004"
LLM_TEMPERATURE = 0.3

# --- RAG Configuration ---
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 5
CONFIDENCE_THRESHOLD = 0.6  # Below this, escalate to human

# --- API Configuration ---
API_HOST = "0.0.0.0"
API_PORT = 8000
