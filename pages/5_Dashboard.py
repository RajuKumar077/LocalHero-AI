"""
pages/5_Dashboard.py — Community issue analytics dashboard
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.db import get_all_issues, get_stats, initialize_db

st.set_page_config(
    page_title="Dashboard — LocalHero AI",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
[data-testid="stSidebar"] { background: linear-gradient(180deg,#1a1a2e,#16213e,#0f3460); }
[data-testid="stSidebar"] * { color:#e0e0e0 !important; }
.stat-card {
    background:#fff;
    border-radius:14px;
    padding:24px;
    text-align:center;
    box-shadow:0 2px 12px rgba(0,0,0,0.08);
    border-top:5px solid;
}
.stat-number { font-size:2.4rem; font-weight:800; color:#1a1a2e; }
.stat-label  { font-size:0.9rem; color:#666; margin-top:4px; }
</style>
""", unsafe_allow_html=True)

initialize_db()

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 📊 Community Dashboard")
st.markdown("Real-time analytics of all civic issues reported through LocalHero AI.")
st.markdown("---")

with st.sidebar:
    st.markdown("## 📊 Dashboard")
    st.markdown("This dashboard aggregates all issues stored in the local SQLite database.")
    st.markdown("---")
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()

# ── Fetch data ────────────────────────────────────────────────────────────────
stats = get_stats()
issues = get_all_issues()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="stat-card" style="border-color:#3498db;">
        <div class="stat-number">{stats['total']}</div>
        <div class="stat-label">📋 Total Reports</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-card" style="border-color:#e74c3c;">
        <div class="stat-number">{stats['high_priority']}</div>
        <div class="stat-label">🔴 High Priority Issues</div>
    </div>""", unsafe_allow_html=True)

with c3:
    cat_count = len(stats['category_dist'])
    st.markdown(f"""
    <div class="stat-card" style="border-color:#27ae60;">
        <div class="stat-number">{cat_count}</div>
        <div class="stat-label">📂 Issue Categories</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="stat-card" style="border-color:#f39c12;">
        <div class="stat-number" style="font-size:1.4rem;">{stats['most_common'] or '—'}</div>
        <div class="stat-label">🏆 Most Common Category</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ── No data placeholder ───────────────────────────────────────────────────────
if stats["total"] == 0:
    st.info("📭 No issues have been reported yet. Use the **Report Issue** or **Image Analyzer** pages to submit your first report!")
    st.markdown("### 📌 Getting Started")
    col_a, col_b = st.columns(2)
    col_a.page_link("pages/1_Report_Issue.py", label="📝 Report a Text Issue", icon="📝")
    col_b.page_link("pages/2_Image_Analyzer.py", label="📷 Analyze an Image", icon="📷")
    st.stop()

# ── Charts ────────────────────────────────────────────────────────────────────
df = pd.DataFrame(issues)

SEVERITY_COLOR_MAP = {
    "Low":      "#27ae60",
    "Medium":   "#f39c12",
    "High":     "#e67e22",
    "Critical": "#e74c3c",
}

chart_col1, chart_col2 = st.columns(2)

# ── Category Distribution ─────────────────────────────────────────────────────
with chart_col1:
    st.markdown("### 📂 Issues by Category")
    if stats["category_dist"]:
        cat_df = pd.DataFrame(
            list(stats["category_dist"].items()),
            columns=["Category", "Count"],
        ).sort_values("Count", ascending=False)

        fig_cat = px.bar(
            cat_df,
            x="Count",
            y="Category",
            orientation="h",
            color="Count",
            color_continuous_scale="Blues",
            text="Count",
        )
        fig_cat.update_traces(textposition="outside")
        fig_cat.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=20, t=10, b=10),
            height=350,
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No category data yet.")

# ── Severity Distribution ─────────────────────────────────────────────────────
with chart_col2:
    st.markdown("### ⚠️ Severity Distribution")
    if stats["severity_dist"]:
        sev_df = pd.DataFrame(
            list(stats["severity_dist"].items()),
            columns=["Severity", "Count"],
        )
        colors = [SEVERITY_COLOR_MAP.get(s, "#3498db") for s in sev_df["Severity"]]
        fig_sev = px.pie(
            sev_df,
            values="Count",
            names="Severity",
            color="Severity",
            color_discrete_map=SEVERITY_COLOR_MAP,
            hole=0.4,
        )
        fig_sev.update_traces(textinfo="label+percent+value")
        fig_sev.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=350)
        st.plotly_chart(fig_sev, use_container_width=True)
    else:
        st.info("No severity data yet.")

# ── Timeline ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📅 Reports Over Time")

try:
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    timeline = df.groupby("date").size().reset_index(name="count")
    fig_time = px.line(
        timeline,
        x="date",
        y="count",
        markers=True,
        labels={"date": "Date", "count": "Reports"},
        color_discrete_sequence=["#0f3460"],
    )
    fig_time.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=250)
    st.plotly_chart(fig_time, use_container_width=True)
except Exception:
    st.info("Timeline data unavailable.")

# ── Source type breakdown ─────────────────────────────────────────────────────
st.markdown("---")
c_src1, c_src2 = st.columns(2)

with c_src1:
    st.markdown("### 📥 Report Source")
    if "source_type" in df.columns:
        src = df["source_type"].value_counts().reset_index()
        src.columns = ["Source", "Count"]
        src["Source"] = src["Source"].map({"text": "📝 Text", "image": "📷 Image"}).fillna(src["Source"])
        fig_src = px.bar(src, x="Source", y="Count", color="Source",
                         color_discrete_sequence=["#0f3460", "#533483"])
        fig_src.update_layout(showlegend=False, height=280, margin=dict(l=0,r=0,t=10,b=10))
        st.plotly_chart(fig_src, use_container_width=True)

# ── Recent Reports Table ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📋 Recent Reports")

display_df = df.head(20).copy()

# Severity badge colours in table
def style_severity(val):
    colors = {
        "Low":      "background-color:#d5f5e3; color:#1e8449",
        "Medium":   "background-color:#fef9e7; color:#b7950b",
        "High":     "background-color:#fdebd0; color:#a04000",
        "Critical": "background-color:#fadbd8; color:#922b21",
    }
    return colors.get(val, "")

cols_to_show = ["id", "timestamp", "category", "severity", "authority", "source_type"]
cols_to_show = [c for c in cols_to_show if c in display_df.columns]

styled = (
    display_df[cols_to_show]
    .rename(columns={
        "id": "ID", "timestamp": "Time", "category": "Category",
        "severity": "Severity", "authority": "Authority", "source_type": "Source"
    })
    .style.applymap(style_severity, subset=["Severity"])
)
st.dataframe(styled, use_container_width=True, height=400)

# ── Export ────────────────────────────────────────────────────────────────────
st.markdown("---")
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Export All Reports as CSV",
    data=csv,
    file_name="localhero_reports.csv",
    mime="text/csv",
)
