"""
pages/3_Knowledge_Assistant.py — RAG-powered civic Q&A
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="Knowledge Assistant — LocalHero AI",
    page_icon="🧠",
    layout="wide",
)

st.markdown("""
<style>
[data-testid="stSidebar"] { background: linear-gradient(180deg,#1a1a2e,#16213e,#0f3460); }
[data-testid="stSidebar"] * { color:#e0e0e0 !important; }
.answer-box {
    background: linear-gradient(135deg, #f8f9ff 0%, #eef2ff 100%);
    border-radius: 14px;
    padding: 24px;
    border-left: 5px solid #3498db;
    margin-bottom: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.context-box {
    background: #fafafa;
    border-radius: 10px;
    padding: 16px;
    border: 1px solid #e0e0e0;
    font-size: 0.88rem;
    color: #555;
}
.q-chip {
    display:inline-block;
    background:#1a1a2e;
    color:#fff !important;
    border-radius:99px;
    padding:5px 16px;
    font-size:0.88rem;
    margin:4px;
    cursor:pointer;
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 🧠 Knowledge Assistant")
st.markdown("Ask any question about civic services, government helplines, or complaint procedures. Powered by **RAG + Gemini**.")
st.markdown("---")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 Knowledge Assistant")
    st.markdown("**Knowledge base includes:**")
    st.markdown("""
- 📋 Municipal Services Guide
- 🗑️ Sanitation Department
- 💧 Water Supply Department
- 🛣️ Road Maintenance
- 📞 Emergency Contacts
- 🏛️ Government Schemes
""")
    st.markdown("---")
    if st.button("🔄 Rebuild Knowledge Base", use_container_width=True):
        with st.spinner("Rebuilding FAISS index…"):
            try:
                from rag.retrieval import rebuild_index
                msg = rebuild_index()
                st.success(msg)
            except Exception as e:
                st.error(f"Failed: {e}")

# ── Example questions ─────────────────────────────────────────────────────────
EXAMPLES = [
    "Who handles water leakage complaints?",
    "What is the emergency helpline number?",
    "How do I report a broken streetlight?",
    "What is the Swachh Bharat Mission?",
    "How can I get a new water connection?",
    "What are the rights of citizens under the Right to Service Act?",
    "How do I complain about a pothole?",
    "What is the AMRUT scheme?",
    "Who is responsible for road maintenance in cities?",
]

st.markdown("**💡 Try these questions:**")
cols = st.columns(3)
for i, q in enumerate(EXAMPLES):
    if cols[i % 3].button(q, key=f"eq_{i}", use_container_width=True):
        st.session_state["kg_question"] = q

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("---")
question = st.text_input(
    "Your question:",
    value=st.session_state.get("kg_question", ""),
    placeholder="e.g. Who handles water leakage complaints?",
)

ask_btn = st.button("🔍 Ask", type="primary")

# ── Answer ────────────────────────────────────────────────────────────────────
if ask_btn or st.session_state.get("kg_question"):
    q = question.strip() or st.session_state.get("kg_question", "")
    if not q:
        st.warning("Please enter a question.")
    else:
        # Clear the prefill after use
        if "kg_question" in st.session_state:
            del st.session_state["kg_question"]

        with st.spinner("🔍 Searching knowledge base and consulting Gemini…"):
            try:
                from rag.retrieval import answer_question
                answer, context = answer_question(q)

                st.markdown(f"**❓ Question:** {q}")
                st.markdown(f"""
<div class="answer-box">
<strong>🤖 AI Answer:</strong><br><br>{answer.replace(chr(10), '<br>')}
</div>
""", unsafe_allow_html=True)

                with st.expander("📚 Retrieved Context (from knowledge base)"):
                    st.markdown(f"""<div class="context-box">{context.replace(chr(10), '<br>')}</div>""",
                                unsafe_allow_html=True)

            except FileNotFoundError as fe:
                st.error(f"📁 Knowledge base not found: {fe}")
                st.info("The FAISS index will be built automatically on first run. Ensure the `data/` directory contains .txt files.")
            except ValueError as ve:
                st.error(f"🔑 API Key Error: {ve}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.info("This may take a moment on first run while the knowledge base index is built.")
