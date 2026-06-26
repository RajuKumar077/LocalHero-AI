"""
pages/4_Complaint_Generator.py — Generate formal civic complaint letters
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from datetime import date
import io

st.set_page_config(
    page_title="Complaint Generator — LocalHero AI",
    page_icon="✉️",
    layout="wide",
)

st.markdown("""
<style>
[data-testid="stSidebar"] { background: linear-gradient(180deg,#1a1a2e,#16213e,#0f3460); }
[data-testid="stSidebar"] * { color:#e0e0e0 !important; }
.letter-box {
    background: #fffef9;
    border-radius: 14px;
    padding: 32px 36px;
    border: 1px solid #e8e0c0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    font-family: 'Georgia', serif;
    line-height: 1.8;
    white-space: pre-wrap;
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# ✉️ Complaint Letter Generator")
st.markdown("Generate a professional, ready-to-send formal complaint letter for any civic issue.")
st.markdown("---")

with st.sidebar:
    st.markdown("## ✉️ Complaint Generator")
    st.markdown("**How to use:**")
    st.markdown("""
1. Describe the issue (or auto-fill from Report Issue page)
2. Enter the location details
3. Optionally add your name
4. Click Generate Letter
5. Copy or download the letter
""")
    st.markdown("---")
    st.markdown("**After generating:**")
    st.markdown("""
- Send to your Ward Office
- Email the Municipal Commissioner
- Post on citizen grievance portals
- Attach to your complaint on pgportal.gov.in
""")

# ── Pre-fill from session state if navigated from Report Issue page ───────────
prefill_issue = st.session_state.get("last_issue", "")

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([2, 1])

with col1:
    issue_desc = st.text_area(
        "📋 Issue Description",
        value=prefill_issue,
        height=140,
        placeholder="Describe the civic issue clearly. E.g. There is a large garbage pile near the bus stand at MG Road that has been present for over 3 days, blocking pedestrian access and causing a foul smell.",
    )

with col2:
    location = st.text_input(
        "📍 Location",
        placeholder="e.g. MG Road, near Bus Stand, Ward 12, Bengaluru",
    )
    citizen_name = st.text_input(
        "👤 Your Name (optional)",
        placeholder="e.g. Rahul Sharma",
    )
    st.markdown(f"📅 **Date:** {date.today().strftime('%d %B %Y')}")

generate_btn = st.button("✉️ Generate Complaint Letter", type="primary", use_container_width=True)

# ── Generation ────────────────────────────────────────────────────────────────
if generate_btn:
    if not issue_desc.strip():
        st.error("⚠️ Please enter an issue description.")
    elif not location.strip():
        st.error("⚠️ Please enter the location of the issue.")
    else:
        with st.spinner("🤖 Generating your formal complaint letter…"):
            try:
                from ai.gemini_client import generate_complaint_letter
                letter = generate_complaint_letter(
                    issue=issue_desc,
                    location=location,
                    citizen_name=citizen_name,
                )

                st.success("✅ Complaint letter generated!")
                st.markdown("---")
                st.markdown("### 📄 Your Complaint Letter")

                # Display letter
                st.markdown(letter)

                st.markdown("---")
                st.markdown("### 📥 Download / Copy")

                col_copy, col_txt, col_pdf = st.columns(3)

                # Plain-text download
                with col_txt:
                    st.download_button(
                        label="⬇️ Download as TXT",
                        data=letter.encode("utf-8"),
                        file_name=f"complaint_letter_{date.today().isoformat()}.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )

                # PDF download
                with col_pdf:
                    try:
                        from fpdf import FPDF

                        class PDF(FPDF):
                            def header(self):
                                self.set_font("Helvetica", "B", 14)
                                self.cell(0, 10, "LocalHero AI — Civic Complaint Letter", align="C")
                                self.ln(10)

                        pdf = PDF()
                        pdf.add_page()
                        pdf.set_font("Helvetica", size=11)
                        pdf.set_margins(20, 20, 20)

                        # Strip markdown bold markers for clean PDF
                        import re
                        clean = re.sub(r"\*\*(.+?)\*\*", r"\1", letter)
                        clean = re.sub(r"#+\s*", "", clean)

                        for line in clean.split("\n"):
                            pdf.multi_cell(0, 8, line)

                        pdf_bytes = pdf.output()
                        st.download_button(
                            label="⬇️ Download as PDF",
                            data=bytes(pdf_bytes),
                            file_name=f"complaint_letter_{date.today().isoformat()}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    except ImportError:
                        st.info("Install `fpdf2` to enable PDF downloads.")
                    except Exception as pdf_err:
                        st.warning(f"PDF generation failed: {pdf_err}. TXT download still available.")

                with col_copy:
                    st.text_area(
                        "📋 Copy Letter Text",
                        value=letter,
                        height=120,
                        help="Select all text here and copy (Ctrl+A, Ctrl+C)",
                    )

            except ValueError as ve:
                st.error(f"🔑 API Key Error: {ve}")
            except Exception as e:
                st.error(f"❌ Letter generation failed: {e}")
