"""
╔══════════════════════════════════════════════════════════════╗
║   Q1 2026 EXECUTIVE SALES INTELLIGENCE DASHBOARD             ║
║   Production-Grade · Executive & Regional Leadership View    ║
╚══════════════════════════════════════════════════════════════╝

Run:
    pip install streamlit pandas plotly openpyxl
    streamlit run q1_executive_dashboard.py

Place your CSV in the same directory, or upload via the sidebar.
"""

# ─── Standard library ────────────────────────────────────────────────────────
import io
import re
import warnings
warnings.filterwarnings("ignore")

# ─── Third-party ─────────────────────────────────────────────────────────────
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
# 0 · PAGE BOOTSTRAP
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Q1 2026 | Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# 1 · DESIGN SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
PALETTE = {
    "bg_main":       "#070B14",
    "bg_card":       "#0D1525",
    "bg_card_hover": "#111C30",
    "bg_subtle":     "#111928",
    "border":        "#1E2D45",
    "border_bright": "#2A3F5F",
    "text_primary":  "#E8EDF5",
    "text_secondary":"#7A8BAD",
    "text_muted":    "#4A5568",
    "accent_blue":   "#3B7DD8",
    "accent_teal":   "#0EA5A0",
    "accent_green":  "#22C55E",
    "accent_amber":  "#F59E0B",
    "accent_red":    "#EF4444",
    "accent_purple": "#8B5CF6",
    "gold":          "#F0C040",
    "chart_1":       "#3B7DD8",
    "chart_2":       "#0EA5A0",
    "chart_3":       "#8B5CF6",
    "chart_4":       "#F59E0B",
    "chart_5":       "#EF4444",
}

PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0D1525",
        font=dict(color=PALETTE["text_secondary"], family="Inter, system-ui, sans-serif"),
        colorway=[PALETTE["chart_1"], PALETTE["chart_2"], PALETTE["chart_3"],
                  PALETTE["chart_4"], PALETTE["chart_5"]],
        xaxis=dict(gridcolor="#1E2D45", linecolor="#1E2D45",
                   tickfont=dict(color=PALETTE["text_secondary"])),
        yaxis=dict(gridcolor="#1E2D45", linecolor="#1E2D45",
                   tickfont=dict(color=PALETTE["text_secondary"])),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=PALETTE["text_secondary"])),
        hoverlabel=dict(bgcolor="#1E2D45", bordercolor="#2A3F5F",
                        font=dict(color=PALETTE["text_primary"])),
        margin=dict(l=10, r=10, t=50, b=10),
        title=dict(font=dict(color=PALETTE["text_primary"], size=15)),
    )
)

def apply_theme(fig, height=380):
    fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=height)
    return fig

CSS = f"""
<style>
html, body, [data-testid="stAppViewContainer"] {{ background: {PALETTE['bg_main']}; color: {PALETTE['text_primary']}; }}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stSidebar"] {{ background: {PALETTE['bg_card']}; border-right: 1px solid {PALETTE['border']}; }}
.kpi-wrap {{
    background: {PALETTE['bg_card']}; border: 1px solid {PALETTE['border']};
    border-radius: 14px; padding: 22px 24px 18px; position: relative;
}}
.kpi-value {{ font-size: 28px; font-weight: 800; color: {PALETTE['text_primary']}; }}
.sec-header {{ border-bottom: 1px solid {PALETTE['border']}; padding-bottom: 10px; margin: 28px 0 16px; font-size: 11px; font-weight: 700; text-transform: uppercase; color: {PALETTE['text_muted']}; }}
.leader-row {{ background: {PALETTE['bg_card']}; border: 1px solid {PALETTE['border']}; border-radius: 10px; padding: 12px 16px; margin-bottom: 8px; display: flex; align-items: center; gap: 14px; }}
.badge {{ padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 700; }}
.badge-red {{ background: rgba(239,68,68,0.15); color: {PALETTE['accent_red']}; }}
.badge-green {{ background: rgba(34,197,94,0.15); color: {PALETTE['accent_green']}; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 2 · CONSTANTS & HELPERS
# ══════════════════════════════════════════════════════════════════════════════
Q1_TARGET = 40_319_855_099.94
FIN_COLS = ["SALES", "COMMISSION", "GGR", "NGR", "SB Sales", "SB GGR", "LB Sales", "LB GGR", "GB Sales", "GB GGR", "GR Sales", "GR GGR", "DEPOSITS", "WITHDRAWALS", "EXPENSES", "NET"]
PRODUCTS = {"Sportsbook": ("SB Sales", "SB GGR", "#3B7DD8"), "Lucky Balls": ("LB Sales", "LB GGR", "#F59E0B"), "Global Bet": ("GB Sales", "GB GGR", "#0EA5A0"), "Greentube": ("GR Sales", "GR GGR", "#8B5CF6")}

def ngn(v, full=False):
    if pd.isna(v) or v == 0: return "₦0"
    neg = v < 0
    v = abs(v)
    if not full:
        if v >= 1e9: s = f"₦{v/1e9:,.2f}B"
        elif v >= 1e6: s = f"₦{v/1e6:,.2f}M"
        else: s = f"₦{v:,.0f}"
    else: s = f"₦{v:,.0f}"
    return f"-{s}" if neg else s

def pct(v, denom):
    return f"{v/denom*100:.1f}%" if denom != 0 else "0.0%"

def clean_num(val):
    if pd.isna(val): return 0.0
    s = re.sub(r"[₦,%↑↓\s]", "", str(val)).replace("(", "-").replace(")", "")
    try: return float(s)
    except: return 0.0

def kpi_card(label, value, icon, sub_html="", bar_color="#3B7DD8"):
    return f'<div class="kpi-wrap"><div class="kpi-accent-bar" style="background:{bar_color}"></div><span class="kpi-icon">{icon}</span><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{sub_html}</div></div>'

def sec(title, icon=""): return f'<div class="sec-header"><span>{icon}</span>{title}</div>'

# ══════════════════════════════════════════════════════════════════════════════
# 3 · DATA PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
def parse_one(src, skiprows=9):
    df = pd.read_csv(src, skiprows=skiprows)
    df = df[df["AGENT"].notna()].copy()
    for col in FIN_COLS:
        if col in df.columns: df[col] = df[col].apply(clean_num)
    if "ACTIVE DAYS" in df.columns:
        df["ACTIVE DAYS"] = pd.to_numeric(df["ACTIVE DAYS"].astype(str).str.replace(r"[^\d.]", "", regex=True), errors="coerce").fillna(0).astype(int)
    return df

@st.cache_data
def load_data(payloads, default_path):
    frames = []
    if payloads:
        for b in payloads: frames.append(parse_one(io.BytesIO(b)))
    else:
        try: frames.append(parse_one(default_path))
        except: return None
    return pd.concat(frames, ignore_index=True).drop_duplicates(subset=["AGENT"])

# ══════════════════════════════════════════════════════════════════════════════
# 4 · APP LOGIC
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    uploads = st.file_uploader("Upload CSVs", type=["csv"], accept_multiple_files=True)
    df_raw = load_data(tuple([u.read() for u in uploads]), "GENERAL Q1 REPORT '26 - RUNNING TOTAL Q1 '26.csv")

if df_raw is None:
    st.error("Please upload data.")
    st.stop()

# Profile Tree Filtering
df_scope = df_raw.copy()
sel_reg = st.sidebar.selectbox("Region", ["All"] + sorted(df_raw["REGION"].unique().tolist()))
if sel_reg != "All": df_scope = df_scope[df_scope["REGION"] == sel_reg]

tab_exec, tab_prod, tab_quad, tab_lead = st.tabs(["📋 Scorecard", "🎮 Products", "🎯 Quadrant", "🏆 Leaders"])

# --- TAB EXEC ---
with tab_exec:
    st.markdown(sec("Q1 Performance", "📊"), unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    s1.write(kpi_card("Sales", ngn(df_scope["SALES"].sum()), "💰"), unsafe_allow_html=True)
    s2.write(kpi_card("Net Profit", ngn(df_scope["NET"].sum()), "📈"), unsafe_allow_html=True)
    s3.write(kpi_card("GGR", ngn(df_scope["GGR"].sum()), "🎰"), unsafe_allow_html=True)

# --- TAB QUADRANT (FIXED) ---
with tab_quad:
    st.markdown(sec("Profitability Quadrant Analysis", "🎯"), unsafe_allow_html=True)
    
    # Data Cleaning for Chart
    plot_df = df_scope[df_scope["STATUS"] == "ACTIVE"].copy()
    plot_df['SALES'] = pd.to_numeric(plot_df['SALES'], errors='coerce').fillna(0)
    plot_df['NET'] = pd.to_numeric(plot_df['NET'], errors='coerce').fillna(0)
    
    if plot_df.empty:
        st.warning("No active agents found in this scope.")
    else:
        # Calculate Quadrants
        m_sales, m_net = plot_df["SALES"].median(), plot_df["NET"].median()
        def get_q(r):
            if r["SALES"] >= m_sales and r["NET"] >= m_net: return "⭐ Star"
            if r["SALES"] >= m_sales: return "⚡ High Vol"
            if r["NET"] >= m_net: return "💎 Efficient"
            return "⚠️ Underperformer"
        
        plot_df["Quadrant"] = plot_df.apply(get_q, axis=1)
        plot_df["Size_Val"] = plot_df["SALES"].clip(lower=1)

        fig_q = px.scatter(
            plot_df, x="SALES", y="NET", color="Quadrant", size="Size_Val",
            hover_name="AGENT", title="Sales vs Profit Intelligence",
            template="plotly_dark", labels={"SALES": "Sales (₦)", "NET": "Profit (₦)"}
        )
        fig_q.add_vline(x=m_sales, line_dash="dash", line_color="#4A5568")
        fig_q.add_hline(y=m_net, line_dash="dash", line_color="#4A5568")
        st.plotly_chart(apply_theme(fig_q, 500), use_container_width=True)

# --- TAB LEADERS ---
with tab_lead:
    st.markdown(sec("Top Performers", "🏆"), unsafe_allow_html=True)
    st.dataframe(df_scope.nlargest(10, "NET")[["AGENT", "MANAGER", "SALES", "NET"]], use_container_width=True)

st.sidebar.caption("v2.1 Production Fix")
