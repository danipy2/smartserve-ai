"""
SmartServe AI — Analytics Dashboard Page
View performance metrics, conversation stats, and improvement opportunities.
"""

import streamlit as st
from pathlib import Path

# Must be first Streamlit command
st.set_page_config(
    page_title="Analytics — SmartServe AI", page_icon="📊", layout="wide"
)

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db import get_analytics, init_db
import config

init_db()

# ── Global Styles ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
  #MainMenu, footer { visibility: hidden; }

  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #164e63 100%);
  }
  section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

  .page-header {
    background: linear-gradient(135deg, #0c4a6e 0%, #0369a1 60%, #0ea5e9 100%);
    border-radius: 16px; padding: 1.6rem 2rem;
    color: white; margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 1rem;
  }
  .page-header .icon { font-size: 2.5rem; }
  .page-header h1 { font-size: 1.8rem; font-weight: 800; margin: 0 0 0.2rem; }
  .page-header p  { margin: 0; opacity: 0.85; font-size: 0.95rem; }

  .kpi-card {
    background: white;
    border: 1px solid #e0f2fe;
    border-top: 4px solid #0ea5e9;
    border-radius: 14px; padding: 1.2rem 1.5rem;
    box-shadow: 0 4px 16px rgba(14,165,233,0.08);
    text-align: center;
  }
  .kpi-card .val { font-size: 2.4rem; font-weight: 800; color: #0c4a6e; }
  .kpi-card .lbl { font-size: 0.82rem; color: #64748b; margin-top: 0.2rem; font-weight: 500; }

  .kpi-card-danger {
    border-top-color: #ef4444;
  }
  .kpi-card-danger .val { color: #b91c1c; }

  .kpi-card-success {
    border-top-color: #22c55e;
  }
  .kpi-card-success .val { color: #166534; }

  .section-title {
    font-size: 1.15rem; font-weight: 700;
    color: #0c4a6e; border-left: 4px solid #0ea5e9;
    padding-left: 0.8rem; margin: 2rem 0 1rem;
  }

  .chart-panel {
    background: white;
    border: 1px solid #e0f2fe;
    border-radius: 14px; padding: 1.5rem;
    box-shadow: 0 4px 16px rgba(14,165,233,0.06);
  }
  .chart-panel h3 { color: #0c4a6e; font-size: 1rem; font-weight: 700; margin: 0 0 1rem; }

  .conf-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 0.5rem 0; border-bottom: 1px solid #f1f5f9;
    font-size: 0.88rem;
  }
  .conf-row:last-child { border-bottom: none; }
  .conf-row .label { color: #475569; }
  .conf-row .value { font-weight: 700; color: #0c4a6e; }

  .opportunity-card {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-left: 4px solid #f59e0b;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
  }
  .opportunity-card h4 { color: #92400e; font-size: 0.9rem; margin: 0 0 0.3rem; }
  .opportunity-card p  { color: #78350f; font-size: 0.82rem; margin: 0; }

  .system-table {
    width: 100%; border-collapse: collapse;
    font-size: 0.88rem;
  }
  .system-table th {
    background: #0c4a6e; color: white;
    padding: 0.6rem 1rem; text-align: left;
    font-weight: 600;
  }
  .system-table th:first-child { border-radius: 8px 0 0 0; }
  .system-table th:last-child  { border-radius: 0 8px 0 0; }
  .system-table td {
    padding: 0.6rem 1rem;
    border-bottom: 1px solid #e0f2fe;
    color: #1e293b;
  }
  .system-table tr:last-child td { border-bottom: none; }
  .system-table tr:nth-child(even) td { background: #f0f9ff; }

  .status-pill {
    background: #dcfce7; color: #166534;
    border-radius: 20px; padding: 2px 10px;
    font-size: 0.78rem; font-weight: 700;
  }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("## 🧠 SmartServe AI")
    st.markdown("*RAG Support Platform*")
    st.markdown("---")
    st.markdown("### 🗂 Navigation")
    st.markdown("""
    - 🏠 **Overview** — Home
    - 💬 **Chat** — Talk to the AI
    - 📄 **Knowledge Base** — Manage docs
    - 📊 **Analytics** — You are here
    """)
    st.markdown("---")
    st.caption("Built for BESYS Technologies Portfolio")

# --- Page Header ---
st.markdown("""
<div class="page-header">
  <div class="icon">📊</div>
  <div>
    <h1>Analytics Dashboard</h1>
    <p>Monitor AI performance, conversation metrics, and identify knowledge gap opportunities</p>
  </div>
</div>
""", unsafe_allow_html=True)

# Get analytics data
analytics = get_analytics()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Key Performance Metrics</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)

avg_conf = analytics["average_confidence"]
conf_display = f"{avg_conf:.0%}" if avg_conf else "N/A"

esc_rate = (
    analytics["escalation_count"] / max(analytics["total_messages"], 1) * 100
    if analytics["total_messages"] > 0 else 0
)

for col, val, lbl, extra_cls in [
    (k1, analytics["total_conversations"],  "💬 Conversations",   ""),
    (k2, analytics["total_messages"],        "📨 Total Messages",   ""),
    (k3, conf_display,                       "🎯 Avg Confidence",   "kpi-card-success" if avg_conf and avg_conf >= 0.6 else ""),
    (k4, analytics["escalation_count"],      "🚨 Escalations",      "kpi-card-danger" if analytics["escalation_count"] > 0 else ""),
    (k5, analytics["total_documents"],       "📄 KB Documents",    ""),
]:
    cls = f"kpi-card {extra_cls}".strip()
    col.markdown(f"""
    <div class="{cls}">
      <div class="val">{val}</div>
      <div class="lbl">{lbl}</div>
    </div>""", unsafe_allow_html=True)

# ── Charts Row ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📉 Trends & Confidence</div>', unsafe_allow_html=True)
col_left, col_right = st.columns(2)

with col_left:
    st.markdown('<div class="chart-panel"><h3>📈 Daily Message Volume</h3>', unsafe_allow_html=True)
    daily = analytics["daily_messages"]
    if daily:
        import pandas as pd
        df = pd.DataFrame(daily)
        df["date"] = pd.to_datetime(df["date"])
        st.bar_chart(df.set_index("date")["count"], color="#0ea5e9")
    else:
        st.info("No message data yet. Start chatting to see trends!")
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="chart-panel"><h3>🎯 Confidence Overview</h3>', unsafe_allow_html=True)
    if analytics["total_messages"] > 0:
        rows = [
            ("Average Confidence",   conf_display),
            ("Escalation Rate",      f"{esc_rate:.1f}%"),
            ("Total Escalations",    str(analytics["escalation_count"])),
            ("Confidence Threshold", f"{config.CONFIDENCE_THRESHOLD:.0%}"),
            ("Total Responses",      str(analytics["total_messages"])),
        ]
        html_rows = "".join(
            f'<div class="conf-row"><span class="label">{l}</span><span class="value">{v}</span></div>'
            for l, v in rows
        )
        st.markdown(html_rows, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Overall Confidence Level**")
        st.progress(min(avg_conf or 0, 1.0))
    else:
        st.info("No confidence data yet. Start chatting to generate metrics.")
    st.markdown("</div>", unsafe_allow_html=True)

# ── Improvement Opportunities ──────────────────────────────────────────────────
st.markdown('<div class="section-title">🔍 Improvement Opportunities</div>', unsafe_allow_html=True)
st.caption("Low-confidence questions — consider uploading more documents that cover these topics.")

low_conf = analytics["low_confidence_queries"]
if low_conf:
    for i, query_info in enumerate(low_conf, 1):
        with st.expander(
            f"❓ {query_info['question'][:80]}…  (Confidence: {query_info['confidence']:.0%})"
        ):
            st.markdown(f"""
            <div class="opportunity-card">
              <h4>Question #{i}</h4>
              <p>{query_info['question']}</p>
            </div>""", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("Confidence", f"{query_info['confidence']:.0%}")
            c2.metric("Date", query_info["date"][:10])
            c3.metric("Status", "Needs Docs")
            st.info(
                "💡 **Tip:** Upload a document covering this topic to improve accuracy on similar questions."
            )
else:
    st.success(
        "✅ No low-confidence queries found! "
        "The AI is performing well with the current knowledge base."
    )

# ── System Health ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">⚙️ System Health</div>', unsafe_allow_html=True)

col_sys1, col_sys2 = st.columns(2)

with col_sys1:
    st.markdown("""
    <table class="system-table">
      <tr><th>Configuration</th><th>Value</th></tr>
    """ + "".join(f"""
      <tr><td>{k}</td><td><code>{v}</code></td></tr>
    """ for k, v in [
        ("LLM Model",            config.LLM_MODEL),
        ("Embedding Model",      config.EMBEDDING_MODEL),
        ("Confidence Threshold", config.CONFIDENCE_THRESHOLD),
        ("Chunk Size",           config.CHUNK_SIZE),
        ("Chunk Overlap",        config.CHUNK_OVERLAP),
        ("Top K Results",        config.TOP_K_RESULTS),
    ]) + "</table>", unsafe_allow_html=True)

with col_sys2:
    st.markdown("""
    <table class="system-table">
      <tr><th>Component</th><th>Status</th></tr>
      <tr><td>Vector Store</td><td><span class="status-pill">🟢 ChromaDB Online</span></td></tr>
      <tr><td>Database</td><td><span class="status-pill">🟢 SQLite Ready</span></td></tr>
      <tr><td>LLM Provider</td><td><span class="status-pill">🟢 Google Gemini</span></td></tr>
      <tr><td>RAG Pipeline</td><td><span class="status-pill">🟢 Active</span></td></tr>
      <tr><td>Embedding API</td><td><span class="status-pill">🟢 Connected</span></td></tr>
      <tr><td>API Key</td><td><span class="status-pill">🟢 Configured</span></td></tr>
    </table>
    """, unsafe_allow_html=True)
