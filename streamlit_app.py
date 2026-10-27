"""
SmartServe AI â€” Streamlit Application
Main entry point for the Streamlit frontend.
"""

import os
import streamlit as st

st.set_page_config(
    page_title="SmartServe AI",
    page_icon="ðŸ§ ",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load secrets â€” works on both Streamlit Cloud and Render.com
try:
    if "GOOGLE_API_KEY" in st.secrets:
        os.environ.setdefault("GOOGLE_API_KEY", st.secrets["GOOGLE_API_KEY"])
except Exception:
    pass  # On Render.com, env vars are already set directly

if not os.environ.get("GOOGLE_API_KEY"):
    st.error("âš ï¸ **GOOGLE_API_KEY not configured.** Add it as an Environment Variable on Render.com.")
    st.stop()

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  #MainMenu, footer { visibility: hidden; }

  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #164e63 100%);
  }
  section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

  .hero {
    background: linear-gradient(135deg, #0c4a6e 0%, #0369a1 60%, #0ea5e9 100%);
    border-radius: 20px; padding: 2.5rem;
    color: white; margin-bottom: 1.5rem;
    position: relative; overflow: hidden;
  }
  .hero::before {
    content: 'ðŸ§ ';
    position: absolute; right: 2rem; top: 50%;
    transform: translateY(-50%);
    font-size: 9rem; opacity: 0.08;
  }
  .hero h1 { font-size: 2.4rem; font-weight: 800; margin: 0 0 0.5rem; }
  .hero p  { opacity: 0.88; margin: 0; font-size: 1.05rem; max-width: 65%; }

  .badge {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.3);
    color: white; border-radius: 20px;
    padding: 4px 14px; font-size: 0.78rem;
    font-weight: 600; margin: 4px 3px 0 0;
  }

  .feature-card {
    background: white;
    border: 1px solid #e0f2fe;
    border-top: 4px solid #0ea5e9;
    border-radius: 14px; padding: 1.5rem;
    box-shadow: 0 4px 16px rgba(14,165,233,0.08);
    height: 100%;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(14,165,233,0.15);
  }
  .feature-card .icon { font-size: 2rem; margin-bottom: 0.8rem; }
  .feature-card h3   { font-size: 1rem; font-weight: 700; color: #0c4a6e; margin: 0 0 0.5rem; }
  .feature-card p    { font-size: 0.85rem; color: #64748b; margin: 0; line-height: 1.5; }

  .flow-step {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
    display: flex; align-items: flex-start; gap: 1rem;
  }
  .flow-step .num {
    background: #0ea5e9; color: white;
    border-radius: 50%; width: 28px; height: 28px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.85rem; flex-shrink: 0;
  }
  .flow-step .txt h4 { margin: 0 0 2px; font-size: 0.9rem; color: #0c4a6e; }
  .flow-step .txt p  { margin: 0; font-size: 0.8rem; color: #64748b; }

  .tech-chip {
    display: inline-block;
    background: #f0f9ff; border: 1px solid #bae6fd;
    color: #0369a1; border-radius: 8px;
    padding: 5px 14px; font-size: 0.82rem;
    font-weight: 600; margin: 4px;
  }

  .section-title {
    font-size: 1.35rem; font-weight: 700;
    color: #0c4a6e; border-left: 4px solid #0ea5e9;
    padding-left: 0.8rem; margin: 2rem 0 1.2rem;
  }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ðŸ§  SmartServe AI")
    st.markdown("*RAG Support Platform*")
    st.markdown("---")
    st.markdown("### ðŸ—‚ Navigation")
    st.markdown("""
    - ðŸ  **Overview** â€” You are here
    - ðŸ’¬ **Chat** â€” Talk to the AI
    - ðŸ“„ **Knowledge Base** â€” Manage docs
    - ðŸ“Š **Analytics** â€” Performance metrics
    """)
    st.markdown("---")
    st.markdown("### âš™ï¸ Tech Stack")
    for t in ["LangChain","Gemini AI","ChromaDB","FastAPI","Streamlit","SQLite"]:
        st.markdown(f"<span style='background:rgba(255,255,255,0.1);border-radius:6px;padding:2px 10px;font-size:0.82rem;display:inline-block;margin:2px'>âš™ï¸ {t}</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Built as a portfolio project")

# Hero
st.markdown("""
<div class="hero">
  <h1>ðŸ§  SmartServe AI</h1>
  <p>RAG-powered customer support platform. Upload your documents and get an intelligent chatbot
     that answers questions with citations, confidence scoring, and smart escalation.</p>
  <div style="margin-top:1.2rem">
    <span class="badge">ðŸ” Semantic Search</span>
    <span class="badge">ðŸ“„ PDF & DOCX</span>
    <span class="badge">ðŸŽ¯ Confidence Scoring</span>
    <span class="badge">ðŸ”— Source Citations</span>
    <span class="badge">ðŸ‘¤ Auto Escalation</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Feature cards
st.markdown('<div class="section-title">âœ¨ Key Features</div>', unsafe_allow_html=True)
f1, f2, f3 = st.columns(3)
features = [
    (f1, "ðŸ“„", "Document Intelligence",
     "Upload PDFs and Word docs. The AI chunks, embeds, and indexes them into a vector store for instant retrieval."),
    (f2, "ðŸŽ¯", "Confidence Scoring",
     "Every answer is scored 0â€“100%. Below 60%, the question auto-escalates to a human agent â€” no wrong answers."),
    (f3, "ðŸ”—", "Source Citations",
     "Every response shows which document and section the information came from, so users can verify answers."),
]
for col, icon, title, desc in features:
    col.markdown(f"""
    <div class="feature-card">
      <div class="icon">{icon}</div>
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# RAG Pipeline
st.markdown('<div class="section-title">ðŸ”„ How RAG Works</div>', unsafe_allow_html=True)
col_a, col_b = st.columns(2)
steps = [
    ("ðŸ“„ Upload Documents",    "PDF and DOCX files ingested via the Knowledge Base page"),
    ("âœ‚ï¸ Chunking",           "Documents split into 1,000-char overlapping chunks"),
    ("ðŸ”¢ Embedding",          "Each chunk embedded via Gemini text-embedding-004"),
    ("ðŸ—„ï¸ Vector Store",       "Embeddings stored in ChromaDB for fast similarity search"),
    ("ðŸ’¬ User Question",       "Customer asks a question in natural language"),
    ("ðŸ” Semantic Search",     "Top-5 most relevant chunks retrieved from ChromaDB"),
    ("ðŸ§  LLM Generation",      "Gemini generates answer grounded in retrieved context"),
    ("ðŸ“Š Confidence Score",    "LLM self-evaluates confidence â†’ escalate if < 60%"),
]
for i, (title, desc) in enumerate(steps):
    col = col_a if i % 2 == 0 else col_b
    col.markdown(f"""
    <div class="flow-step">
      <div class="num">{i+1}</div>
      <div class="txt"><h4>{title}</h4><p>{desc}</p></div>
    </div>""", unsafe_allow_html=True)

# Tech stack
st.markdown('<div class="section-title">ðŸ› ï¸ Tech Stack</div>', unsafe_allow_html=True)
techs = ["ðŸ”— LangChain 0.3", "â™Š Gemini 3.8 Flash", "ðŸ—„ï¸ ChromaDB", "âš¡ FastAPI",
         "ðŸŽˆ Streamlit", "ðŸ—ƒï¸ SQLite", "ðŸ“„ PyPDF", "ðŸ“ python-docx"]
st.markdown("".join(f'<span class="tech-chip">{t}</span>' for t in techs), unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.info("ðŸ‘ˆ Start by going to **ðŸ“„ Knowledge Base** to upload documents, then use **ðŸ’¬ Chat** to ask questions!")

# Demo-ready callout
st.markdown("""
<div style="background:linear-gradient(135deg,#064e3b,#065f46);border:1px solid #34d399;border-radius:14px;padding:1.4rem 1.8rem;">
  <strong style="color:#6ee7b7;font-size:1rem">🚀 Demo-Ready — No Setup Needed!</strong><br>
  <span style="color:#a7f3d0;font-size:0.88rem">A <strong>BizCorp Ethiopia Customer Support Knowledge Base</strong> is pre-loaded automatically. Head to <strong>💬 Chat</strong> and start asking questions instantly — no upload needed. Want to test your own document? Go to 📄 Knowledge Base and upload any PDF, DOCX or TXT.</span>
</div>
""", unsafe_allow_html=True)
