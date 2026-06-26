"""
LocalHero AI — Main entry point
"""

import streamlit as st
from pathlib import Path

# ── Page config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="LocalHero AI",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ---- sidebar ---- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
}
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }

/* ---- hero banner ---- */
.hero-banner {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 50%, #533483 100%);
    border-radius: 16px;
    padding: 48px 40px;
    margin-bottom: 32px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.hero-banner h1 { font-size: 3rem; color: #ffffff; margin: 0 0 8px 0; }
.hero-banner p  { font-size: 1.2rem; color: #a0c4ff; margin: 0; }

/* ---- feature cards ---- */
.feature-grid { display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 32px; }
.feature-card {
    flex: 1; min-width: 180px;
    background: #ffffff;
    border-radius: 14px;
    padding: 28px 22px;
    text-align: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    border-top: 4px solid;
    transition: transform .2s;
}
.feature-card:hover { transform: translateY(-4px); }
.feature-card .icon { font-size: 2.4rem; margin-bottom: 12px; }
.feature-card h3   { font-size: 1rem; font-weight: 700; margin: 0 0 8px 0; color: #1a1a2e; }
.feature-card p    { font-size: 0.85rem; color: #555; margin: 0; }

/* ── stat cards ── */
.stat-card {
    background: #ffffff;
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    border-left: 5px solid;
}
</style>
""", unsafe_allow_html=True)

# ── Ensure required directories exist ─────────────────────────────────────
for folder in ["uploads", "assets", "data", "database"]:
    Path(folder).mkdir(exist_ok=True)

# ── Hero Banner ────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <h1>🏘️ LocalHero AI</h1>
    <p>AI-powered hyperlocal civic issue resolver — built for citizens, powered by Gemini</p>
</div>
""", unsafe_allow_html=True)

# ── Feature Cards ──────────────────────────────────────────────────────────
st.markdown("""
<div class="feature-grid">
    <div class="feature-card" style="border-color:#e74c3c;">
        <div class="icon">📝</div>
        <h3>Report Issue</h3>
        <p>Describe any civic problem and get instant AI analysis with severity rating</p>
    </div>
    <div class="feature-card" style="border-color:#f39c12;">
        <div class="icon">📷</div>
        <h3>Image Analyzer</h3>
        <p>Upload a photo — Gemini Vision identifies the issue and recommends action</p>
    </div>
    <div class="feature-card" style="border-color:#27ae60;">
        <div class="icon">🧠</div>
        <h3>Knowledge Assistant</h3>
        <p>RAG-powered Q&A on civic services, helplines, and government schemes</p>
    </div>
    <div class="feature-card" style="border-color:#2980b9;">
        <div class="icon">✉️</div>
        <h3>Complaint Generator</h3>
        <p>Auto-generate formal complaint letters ready to send to authorities</p>
    </div>
    <div class="feature-card" style="border-color:#8e44ad;">
        <div class="icon">📊</div>
        <h3>Dashboard</h3>
        <p>Visual analytics of all reported issues across your community</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── How It Works ───────────────────────────────────────────────────────────
st.markdown("## 🚀 How It Works")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.info("**Step 1** 📝\n\nDescribe or photograph a civic issue in your neighbourhood")
with c2:
    st.info("**Step 2** 🤖\n\nGemini 2.5 Flash analyses severity, category & responsible authority")
with c3:
    st.info("**Step 3** ✉️\n\nGenerate a professional complaint letter in one click")
with c4:
    st.info("**Step 4** 📊\n\nTrack all community reports on the live dashboard")

st.markdown("---")

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏘️ LocalHero AI")
    st.markdown("*Hyperlocal Problem Solver*")
    st.markdown("---")
    st.markdown("### 📌 Navigation")
    st.markdown("Use the **Pages** menu above to navigate between sections.")
    st.markdown("---")
    st.markdown("### 🤖 Powered by")
    st.markdown("- **Gemini 2.5 Flash** — Issue analysis & letter generation")
    st.markdown("- **LangChain + FAISS** — RAG knowledge retrieval")
    st.markdown("- **Sentence Transformers** — Semantic embeddings")
    st.markdown("- **SQLite** — Local report storage")
    st.markdown("---")
    st.markdown("### ℹ️ Version")
    st.markdown("`v1.0.0` — Hackathon Edition")

st.markdown("""
<div style="text-align:center; padding: 20px; color: #888; font-size: 0.85rem;">
    Built with ❤️ for the <strong>Community Hero — Hyperlocal Problem Solver</strong> hackathon track<br>
    Powered by Google Gemini 2.5 Flash via Google AI Studio
</div>
""", unsafe_allow_html=True)
