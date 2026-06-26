"""
pages/2_Image_Analyzer.py — Image-based civic issue analysis via Gemini Vision
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import uuid
from pathlib import Path
import streamlit as st
from PIL import Image
import io

from database.db import save_issue, initialize_db

st.set_page_config(page_title="Image Analyzer — LocalHero AI", page_icon="📷", layout="wide")

st.markdown("""
<style>
[data-testid="stSidebar"] { background: linear-gradient(180deg,#1a1a2e,#16213e,#0f3460); }
[data-testid="stSidebar"] * { color:#e0e0e0 !important; }
.result-card {
    background:#fff; border-radius:14px; padding:20px 24px;
    margin-bottom:14px; box-shadow:0 2px 12px rgba(0,0,0,0.08); border-left:5px solid;
}
.sev-low      { border-color:#27ae60; }
.sev-medium   { border-color:#f39c12; }
.sev-high     { border-color:#e67e22; }
.sev-critical { border-color:#e74c3c; }
.sev-default  { border-color:#3498db; }
.card-label { font-size:0.78rem; font-weight:700; text-transform:uppercase; color:#888; margin-bottom:4px; }
.card-value { font-size:1rem; color:#1a1a2e; }
</style>
""", unsafe_allow_html=True)

initialize_db()

UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

SEVERITY_MAP = {
    "low":      ("#27ae60", "sev-low",      "🟢"),
    "medium":   ("#f39c12", "sev-medium",   "🟡"),
    "high":     ("#e67e22", "sev-high",     "🟠"),
    "critical": ("#e74c3c", "sev-critical", "🔴"),
}

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 📷 Image Analyzer")
st.markdown("Upload a photo of a civic problem and let Gemini Vision identify the issue, severity, and recommended action.")
st.markdown("---")

with st.sidebar:
    st.markdown("## 📷 Image Analyzer")
    st.markdown("**Best practices:**")
    st.markdown("""
- Ensure the issue is clearly visible
- Good lighting improves accuracy
- Capture the surrounding context
- Supported: JPG, JPEG, PNG
""")
    st.markdown("---")
    st.markdown("**What can be detected?**")
    st.markdown("""
- 🗑️ Garbage / waste dumps
- 🕳️ Potholes and road damage
- 💧 Water leakage / flooding
- 🚧 Infrastructure damage
- 🌊 Sewage overflow
- 💡 Broken streetlights
- 🌳 Fallen trees blocking roads
""")

# ── Upload section ───────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload an image of the civic issue",
    type=["jpg", "jpeg", "png"],
    help="Maximum file size: 10 MB",
)

if uploaded_file:
    # Validate file size (<10MB)
    file_bytes = uploaded_file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        st.error("❌ File too large. Please upload an image smaller than 10 MB.")
        st.stop()

    img = Image.open(io.BytesIO(file_bytes))

    col_img, col_info = st.columns([1, 1])
    with col_img:
        st.image(img, caption="📸 Uploaded Image", use_container_width=True)
    with col_info:
        st.markdown("**Image Details**")
        st.info(f"""
- 📁 **Filename:** {uploaded_file.name}
- 📐 **Dimensions:** {img.width} × {img.height} px
- 🎨 **Mode:** {img.mode}
- 📦 **Size:** {len(file_bytes) / 1024:.1f} KB
""")

    analyze_btn = st.button("🔍 Analyze Image", type="primary", use_container_width=False)

    if analyze_btn:
        # Determine MIME type
        ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
        mime = "image/png" if ext == "png" else "image/jpeg"

        with st.spinner("🤖 Gemini Vision is examining the image…"):
            try:
                from ai.gemini_client import analyze_image_issue
                result = analyze_image_issue(file_bytes, mime_type=mime)

                # Save image to disk
                save_name = f"{uuid.uuid4().hex[:8]}_{uploaded_file.name}"
                save_path = UPLOADS_DIR / save_name
                with open(save_path, "wb") as f:
                    f.write(file_bytes)

                # ── Parse response ──────────────────────────────────────────
                def _field(label):
                    m = re.search(rf"\*\*{re.escape(label)}:\*\*\s*(.+)", result)
                    return m.group(1).strip() if m else ""

                issue_type   = _field("Issue Type")
                severity     = _field("Severity")
                resp_dept    = _field("Responsible Department")
                action       = _field("Suggested Action")
                risk         = _field("Risk Assessment")
                urgency      = _field("Urgency")
                next_steps   = _field("Citizen Next Steps")

                sev_key = severity.lower()
                _, sev_class, sev_emoji = SEVERITY_MAP.get(
                    sev_key, ("#3498db", "sev-default", "🔵")
                )

                if "no civic issue detected" in result.lower():
                    st.info("ℹ️ No civic issue was detected in this image. Please upload an image showing a public infrastructure or community problem.")
                else:
                    st.success("✅ Image analyzed successfully!")

                    # Metric row
                    m1, m2, m3 = st.columns(3)
                    m1.metric("🚨 Issue Type", issue_type or "—")
                    m2.metric("⚠️ Severity", f"{sev_emoji} {severity}")
                    m3.metric("⏰ Urgency", urgency or "—")

                    st.markdown("---")

                    def card(lbl, val, css="sev-default"):
                        if not val:
                            return
                        st.markdown(f"""
                        <div class="result-card {css}">
                            <div class="card-label">{lbl}</div>
                            <div class="card-value">{val}</div>
                        </div>""", unsafe_allow_html=True)

                    card("🏛️ Responsible Department", resp_dept, sev_class)
                    card("🛠️ Suggested Action", action, sev_class)
                    card("⚠️ Risk Assessment", risk, sev_class)
                    card("🧭 Citizen Next Steps", next_steps, sev_class)

                    with st.expander("📄 Full AI Response"):
                        st.markdown(result)

                    # Save to DB
                    try:
                        issue_id = save_issue(
                            issue_description=f"[Image Upload] {issue_type}",
                            category=issue_type,
                            severity=severity,
                            authority=resp_dept,
                            suggested_action=action,
                            source_type="image",
                            image_path=str(save_path),
                        )
                        st.info(f"💾 Report saved (ID: #{issue_id}). View on the Dashboard page.")
                    except Exception as db_err:
                        st.warning(f"Could not save to database: {db_err}")

                    # Store for complaint generator
                    st.session_state["last_issue"] = f"Image Upload — Issue: {issue_type}. {risk}"
                    st.session_state["last_analysis"] = result

                    st.markdown("---")
                    nc1, nc2 = st.columns(2)
                    nc1.page_link("pages/4_Complaint_Generator.py", label="✉️ Generate Complaint Letter", icon="✉️")
                    nc2.page_link("pages/5_Dashboard.py", label="📊 View Dashboard", icon="📊")

            except ValueError as ve:
                st.error(f"🔑 API Key Error: {ve}")
            except Exception as e:
                st.error(f"❌ Image analysis failed: {e}")
                st.info("Please verify your GEMINI_API_KEY is valid and try again.")
else:
    st.info("👆 Upload an image above to get started.")
