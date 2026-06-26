"""
pages/1_Report_Issue.py — Text-based civic issue analysis
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import streamlit as st
from database.db import save_issue, initialize_db

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Report Issue — LocalHero AI", page_icon="📝", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background: linear-gradient(180deg,#1a1a2e,#16213e,#0f3460); }
[data-testid="stSidebar"] * { color:#e0e0e0 !important; }

.result-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 14px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border-left: 5px solid;
}
.severity-low      { border-color: #27ae60; }
.severity-medium   { border-color: #f39c12; }
.severity-high     { border-color: #e67e22; }
.severity-critical { border-color: #e74c3c; }
.severity-default  { border-color: #3498db; }

.card-label { font-size:0.78rem; font-weight:700; text-transform:uppercase;
              color:#888; letter-spacing:0.06em; margin-bottom:4px; }
.card-value { font-size:1rem; color:#1a1a2e; }
.badge {
    display:inline-block; padding:3px 12px; border-radius:99px;
    font-size:0.8rem; font-weight:700; color:#fff;
}
</style>
""", unsafe_allow_html=True)

initialize_db()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 📝 Report a Civic Issue")
st.markdown("Describe the problem in plain language — Gemini will analyze severity, category, and the responsible authority.")

st.markdown("---")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📝 Report Issue")
    st.markdown("**Tips for a good report:**")
    st.markdown("""
- Be specific about the location
- Describe the size / extent of the problem
- Mention how long the issue has persisted
- Note any safety hazards
""")
    st.markdown("---")
    st.markdown("**Example issues:**")
    examples = [
        "Large garbage pile near the bus stand for 3 days",
        "Deep pothole on MG Road causing accidents",
        "Water leakage from pipe at Sector 5 market",
        "Street lights not working on Nehru Nagar road",
        "Sewage overflow near school entrance",
    ]
    for ex in examples:
        if st.button(f"💡 {ex[:40]}…", key=ex, use_container_width=True):
            st.session_state["prefill"] = ex

# ── Input area ───────────────────────────────────────────────────────────────
prefill = st.session_state.pop("prefill", "")

issue_text = st.text_area(
    "Describe the civic issue:",
    value=prefill,
    height=150,
    placeholder="E.g. There is a large garbage pile near the bus stand that has been accumulating for 3 days. It is blocking pedestrian access and causing a foul smell.",
    help="Be as descriptive as possible — include location details and duration.",
)

col_btn, col_clear = st.columns([1, 5])
with col_btn:
    analyze_clicked = st.button("🔍 Analyze Issue", type="primary", use_container_width=True)
with col_clear:
    clear_clicked = st.button("🗑️ Clear", use_container_width=False)

if clear_clicked:
    st.rerun()

# ── Analysis ─────────────────────────────────────────────────────────────────
SEVERITY_COLORS = {
    "low": ("#27ae60", "severity-low"),
    "medium": ("#f39c12", "severity-medium"),
    "high": ("#e67e22", "severity-high"),
    "critical": ("#e74c3c", "severity-critical"),
}

def _extract_field(text: str, label: str) -> str:
    pattern = rf"\*\*{re.escape(label)}:\*\*\s*(.+)"
    m = re.search(pattern, text)
    return m.group(1).strip() if m else ""


def render_results(raw: str, issue_text: str):
    """Parse the Gemini response and render it as cards."""
    fields = {
        "Category":                  _extract_field(raw, "Issue Category"),
        "Severity":                  _extract_field(raw, "Severity"),
        "Severity Justification":    _extract_field(raw, "Severity Justification"),
        "Responsible Authority":     _extract_field(raw, "Responsible Authority"),
        "Suggested Action":          _extract_field(raw, "Suggested Action"),
        "Citizen Guidance":          _extract_field(raw, "Citizen Guidance"),
        "Estimated Resolution Time": _extract_field(raw, "Estimated Resolution Time"),
    }

    sev_key = fields["Severity"].lower()
    sev_color, sev_class = SEVERITY_COLORS.get(sev_key, ("#3498db", "severity-default"))
    sev_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}.get(sev_key, "🔵")

    st.success("✅ Issue analyzed successfully!")

    # Metric row
    m1, m2, m3 = st.columns(3)
    m1.metric("📂 Category", fields["Category"] or "—")
    m2.metric("⚠️ Severity", f"{sev_emoji} {fields['Severity']}")
    m3.metric("🕐 Resolution", fields["Estimated Resolution Time"] or "—")

    st.markdown("---")

    # Detail cards
    def card(label, value, css_class="severity-default"):
        if not value:
            return
        st.markdown(f"""
        <div class="result-card {css_class}">
            <div class="card-label">{label}</div>
            <div class="card-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)

    card("🏛️ Responsible Authority", fields["Responsible Authority"], sev_class)
    card("🛠️ Suggested Action", fields["Suggested Action"], sev_class)
    card("📋 Severity Justification", fields["Severity Justification"], sev_class)
    card("🧭 Citizen Guidance", fields["Citizen Guidance"], sev_class)

    # Raw response in expander
    with st.expander("📄 Full AI Response"):
        st.markdown(raw)

    # Save to DB
    try:
        issue_id = save_issue(
            issue_description=issue_text,
            category=fields["Category"],
            severity=fields["Severity"],
            authority=fields["Responsible Authority"],
            suggested_action=fields["Suggested Action"],
            source_type="text",
        )
        st.info(f"💾 Report saved to database (ID: #{issue_id}). View on the Dashboard page.")
    except Exception as db_err:
        st.warning(f"Could not save to database: {db_err}")

    return fields


if analyze_clicked:
    if not issue_text.strip():
        st.error("⚠️ Please enter a description of the civic issue before analyzing.")
    else:
        with st.spinner("🤖 Gemini is analyzing your report…"):
            try:
                from ai.gemini_client import analyze_text_issue
                result = analyze_text_issue(issue_text)
                render_results(result, issue_text)

                # Store in session for complaint generator hand-off
                st.session_state["last_issue"] = issue_text
                st.session_state["last_analysis"] = result

                st.markdown("---")
                st.markdown("**Next steps:**")
                nc, nc2 = st.columns(2)
                nc.page_link("pages/4_Complaint_Generator.py", label="✉️ Generate Complaint Letter", icon="✉️")
                nc2.page_link("pages/5_Dashboard.py", label="📊 View Dashboard", icon="📊")

            except ValueError as ve:
                st.error(f"🔑 API Key Error: {ve}")
            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")
                st.info("Please check your GEMINI_API_KEY in the .env file and try again.")
