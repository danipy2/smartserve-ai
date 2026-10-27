"""
SmartServe AI — Streamlit Application
Main entry point for the Streamlit frontend.
"""

import os
import streamlit as st

st.set_page_config(
    page_title="SmartServe AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load Streamlit Cloud secrets into env vars ---
if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        border-left: 4px solid #1E88E5;
        margin-bottom: 1rem;
    }
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/chatbot.png", width=80)
    st.title("SmartServe AI")
    st.caption("Intelligent Customer Support Platform")
    st.divider()
    st.markdown("### Navigation")
    st.markdown("""
    - 💬 **Chat** — Talk to the AI assistant
    - 📄 **Knowledge Base** — Manage documents  
    - 📊 **Analytics** — View performance metrics
    """)
    st.divider()
    st.markdown(
        "Built with LangChain, Gemini AI & ChromaDB",
        help="RAG-powered AI customer support platform",
    )

# --- Main Page ---
st.markdown('<p class="main-header">🤖 SmartServe AI</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">'
    'Intelligent Customer Support Agent Platform — '
    'Transform your documents into an AI-powered support chatbot'
    '</p>',
    unsafe_allow_html=True,
)

# Feature cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>📄 Upload Documents</h3>
        <p>Upload your FAQs, manuals, and documents. 
        The AI learns from your knowledge base to answer customer questions accurately.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>💬 AI-Powered Chat</h3>
        <p>Customers ask questions in natural language. 
        The AI retrieves relevant information and generates accurate, cited responses.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>🔒 Smart Escalation</h3>
        <p>When the AI isn't confident, it automatically flags the question 
        for human review — no wrong answers sent to customers.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# How it works
st.markdown("### How It Works")
st.markdown("""
```
📄 Upload Documents  →  🔪 Chunk & Embed  →  🗄️ Store in Vector DB
                                                      ↓
💬 Customer Question  →  🔍 Semantic Search  →  🤖 AI Generates Answer
                                                      ↓
                                              📊 Confidence Score
                                                ↓           ↓
                                           ✅ High        🚨 Low
                                          Auto-reply    Escalate to Human
```
""")

st.divider()

# Tech stack
st.markdown("### Tech Stack")
cols = st.columns(6)
tech = [
    ("🧠", "LangChain"),
    ("✨", "Gemini AI"),
    ("🗄️", "ChromaDB"),
    ("⚡", "FastAPI"),
    ("🎨", "Streamlit"),
    ("📦", "SQLite"),
]
for col, (icon, name) in zip(cols, tech):
    col.metric(label=icon, value=name)

st.divider()
st.markdown(
    "👈 **Get started** by navigating to the **Knowledge Base** page "
    "to upload your first document, then try the **Chat** page!"
)
