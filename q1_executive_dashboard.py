"""
╔══════════════════════════════════════════════════════════════╗
║   Q1 2026 EXECUTIVE SALES INTELLIGENCE DASHBOARD            ║
║   Production-Grade · Executive & Regional Leadership View   ║
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

PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#e2e8f0"},
        "margin": {"l": 10, "r": 10, "t": 40, "b": 10}
    }
}

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
/* ── Global reset ────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {{
    background: {PALETTE['bg_main']};
    font-family: Inter, system-ui, -apple-system, sans-serif;
}}
[data-testid="stHeader"] {{ background: transparent; }}

/* ── Sidebar ─────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: {PALETTE['bg_card']};
    border-right: 1px solid {PALETTE['border']};
}}
[data-testid="stSidebar"] * {{ color: {PALETTE['text_secondary']} !important; }}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{ color: {PALETTE['text_primary']} !important; }}
[data-testid="stSidebar"] .stSelectbox > label,
[data-testid="stSidebar"] .stFileUploader > label {{
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {PALETTE['text_muted']} !important;
}}

/* ── KPI card ─────────────────────────────────────────────────── */
.kpi-wrap {{
    background: {PALETTE['bg_card']};
    border: 1px solid {PALETTE['border']};
    border-radius: 14px;
    padding: 22px 24px 18px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}}
.kpi-wrap:hover {{ border-color: {PALETTE['border_bright']}; }}
.kpi-accent-bar {{
    position: absolute; top: 0; left: 0;
    height: 3px; width: 100%;
}}
.kpi-icon {{
    font-size: 22px; margin-bottom: 10px; display: block;
}}
.kpi-label {{
    font-size: 11px; font-weight: 600;
    letter-spacing: 0.09em; text-transform: uppercase;
    color: {PALETTE['text_muted']}; margin-bottom: 8px;
}}
.kpi-value {{
    font-size: 28px; font-weight: 800;
    color: {PALETTE['text_primary']}; line-height: 1.1;
    letter-spacing: -0.02em;
}}
.kpi-sub {{
    font-size: 12px; margin-top: 8px;
    color: {PALETTE['text_muted']};
}}
.kpi-delta-good  {{ color: {PALETTE['accent_green']}; font-weight: 600; }}
.kpi-delta-warn  {{ color: {PALETTE['accent_amber']}; font-weight: 600; }}
.kpi-delta-bad   {{ color: {PALETTE['accent_red']};   font-weight: 600; }}
.kpi-delta-blue  {{ color: {PALETTE['accent_blue']};  font-weight: 600; }}

/* ── Section header ──────────────────────────────────────────── */
.sec-header {{
    font-size: 11px; font-weight: 700;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: {PALETTE['text_muted']};
    border-bottom: 1px solid {PALETTE['border']};
    padding-bottom: 10px; margin: 28px 0 16px;
    display: flex; align-items: center; gap: 8px;
}}

/* ── Leaderboard rows ────────────────────────────────────────── */
.leader-row {{
    display: flex; align-items: center;
    background: {PALETTE['bg_card']};
    border: 1px solid {PALETTE['border']};
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    gap: 14px;
}}
.leader-rank {{
    font-size: 15px; font-weight: 800;
    color: {PALETTE['text_muted']};
    min-width: 24px; text-align: center;
}}
.leader-rank.gold   {{ color: #F0C040; }}
.leader-rank.silver {{ color: #A0AEC0; }}
.leader-rank.bronze {{ color: #CD7F32; }}
.leader-info {{ flex: 1; }}
.leader-name {{ font-size: 14px; font-weight: 700; color: {PALETTE['text_primary']}; }}
.leader-meta {{ font-size: 11px; color: {PALETTE['text_muted']}; margin-top: 2px; }}
.leader-value {{ font-size: 15px; font-weight: 700; color: {PALETTE['accent_green']}; }}
.leader-value.neg   {{ color: {PALETTE['accent_red']}; }}

/* ── Risk badge ──────────────────────────────────────────────── */
.badge {{
    display: inline-block; padding: 3px 9px;
    border-radius: 20px; font-size: 10px; font-weight: 700;
    letter-spacing: 0.05em; text-transform: uppercase;
}}
.badge-red    {{ background: rgba(239,68,68,0.15); color: {PALETTE['accent_red']}; }}
.badge-amber  {{ background: rgba(245,158,11,0.15); color: {PALETTE['accent_amber']}; }}
.badge-green  {{ background: rgba(34,197,94,0.15);  color: {PALETTE['accent_green']}; }}
.badge-blue   {{ background: rgba(59,125,216,0.15); color: {PALETTE['accent_blue']}; }}

/* ── Search highlight ────────────────────────────────────────── */
.agent-card {{
    background: {PALETTE['bg_subtle']};
    border: 1px solid {PALETTE['accent_blue']};
    border-radius: 12px; padding: 20px 24px;
}}
.agent-card h3 {{ color: {PALETTE['text_primary']}; margin: 0 0 4px; font-size: 20px; }}
.agent-card .sub {{ color: {PALETTE['text_muted']}; font-size: 12px; margin-bottom: 16px; }}
.agent-grid {{
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 12px; margin-top: 14px;
}}
.agent-stat {{ text-align: center; }}
.agent-stat .v {{ font-size: 18px; font-weight: 700; color: {PALETTE['text_primary']}; }}
.agent-stat .l {{ font-size: 10px; text-transform: uppercase;
                  letter-spacing: 0.07em; color: {PALETTE['text_muted']}; margin-top: 2px; }}

/* ── Progress bar ────────────────────────────────────────────── */
.prog-wrap {{ background: {PALETTE['border']}; border-radius: 4px; height: 6px; }}
.prog-fill  {{ border-radius: 4px; height: 6px; transition: width 0.4s; }}

/* ── Tabs ────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background: {PALETTE['bg_card']};
    border-radius: 10px; padding: 4px; gap: 2px;
    border: 1px solid {PALETTE['border']};
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent; border-radius: 8px;
    color: {PALETTE['text_muted']} !important;
    font-size: 13px; font-weight: 600;
    padding: 8px 20px;
    border: none !important;
}}
.stTabs [aria-selected="true"] {{
    background: {PALETTE['bg_subtle']} !important;
    color: {PALETTE['text_primary']} !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    padding: 20px 0 0; background: transparent;
}}

/* ── Dataframe overrides ─────────────────────────────────────── */
[data-testid="stDataFrame"] {{ border-radius: 10px; overflow: hidden; }}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 2 · CONSTANTS & HELPERS
# ══════════════════════════════════════════════════════════════════════════════
Q1_TARGET = 40_319_855_099.94

FIN_COLS = [
    "SALES", "COMMISSION", "GGR", "NGR",
    "SB Sales", "SB GGR", "LB Sales", "LB GGR",
    "GB Sales", "GB GGR", "GR Sales", "GR GGR",
    "DEPOSITS", "WITHDRAWALS", "EXPENSES", "NET",
]

PRODUCTS = {
    "Sportsbook":  ("SB Sales",  "SB GGR",  "#3B7DD8"),
    "Lucky Balls": ("LB Sales",  "LB GGR",  "#F59E0B"),
    "Global Bet":  ("GB Sales",  "GB GGR",  "#0EA5A0"),
    "Greentube":   ("GR Sales",  "GR GGR",  "#8B5CF6"),
}


def ngn(v, full=False):
    """Format a number as Nigerian Naira."""
    if pd.isna(v) or v == 0:
        return "₦0"
    negative = v < 0
    v = abs(v)
    if not full:
        if v >= 1e9:
            s = f"₦{v/1e9:,.2f}B"
        elif v >= 1e6:
            s = f"₦{v/1e6:,.2f}M"
        elif v >= 1e3:
            s = f"₦{v/1e3:,.1f}K"
        else:
            s = f"₦{v:,.0f}"
    else:
        s = f"₦{v:,.0f}"
    return f"-{s}" if negative else s


def pct(v, denom):
    if denom == 0:
        return "0.0%"
    return f"{v/denom*100:.1f}%"


def clean_num(val):
    if pd.isna(val):
        return 0.0
    s = re.sub(r"[₦,%↑↓\s]", "", str(val))
    s = s.replace("(", "-").replace(")", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


def rank_medal(i):
    medals = {1: ("gold", "🥇"), 2: ("silver", "🥈"), 3: ("bronze", "🥉")}
    cls, icon = medals.get(i, ("", f"#{i}"))
    return cls, icon


def kpi_card(label, value, icon, sub_html="", bar_color=None):
    bar_color = bar_color or PALETTE["accent_blue"]
    return f"""
<div class="kpi-wrap">
  <div class="kpi-accent-bar" style="background:{bar_color}"></div>
  <span class="kpi-icon">{icon}</span>
  <div class="kpi-label">{label}</div>
  <div class="kpi-value">{value}</div>
  <div class="kpi-sub">{sub_html}</div>
</div>"""


def sec(title, icon=""):
    return f'<div class="sec-header"><span>{icon}</span>{title}</div>'


def progress_bar(val, max_val, color):
    w = min(100, val / max_val * 100) if max_val > 0 else 0
    return f"""
<div class="prog-wrap">
  <div class="prog-fill" style="width:{w:.1f}%;background:{color}"></div>
</div>"""


# ══════════════════════════════════════════════════════════════════════════════
# 3 · DATA PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
def parse_one(src, skiprows=9):
    """Load a single CSV (Running-Total format) into a clean DataFrame."""
    if isinstance(src, bytes):
        src = io.BytesIO(src)
    df = pd.read_csv(src, skiprows=skiprows, low_memory=False)

    # Drop right-side summary columns and unnamed cols
    drop = [c for c in df.columns if c.endswith(".1") or c.startswith("Unnamed")]
    df.drop(columns=drop, errors="ignore", inplace=True)

    # Keep only agent rows
    df = df[df["AGENT"].notna()].copy()

    # Numeric cleaning
    for col in FIN_COLS:
        if col in df.columns:
            df[col] = df[col].apply(clean_num)

    if "ACTIVE DAYS" in df.columns:
        df["ACTIVE DAYS"] = (
            pd.to_numeric(
                df["ACTIVE DAYS"].apply(lambda x: re.sub(r"[^\d.]", "", str(x))),
                errors="coerce",
            )
            .fillna(0)
            .astype(int)
        )

    for col in ["AGENT", "MANAGER", "SM", "REGION", "STATUS"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df["STATUS"] = df["STATUS"].str.upper()

    # Derived columns
    df["NET_MARGIN"] = np.where(
        df["SALES"] > 0, df["NET"] / df["SALES"] * 100, 0
    )
    df["WITHDRAWAL_RATE"] = np.where(
        df["DEPOSITS"] > 0, df["WITHDRAWALS"] / df["DEPOSITS"] * 100, 0
    )
    return df


@st.cache_data(show_spinner=False)
def load_data(payloads, default_path):
    """Merge multiple uploaded files OR fall back to local CSV."""
    frames = []
    if payloads:
        for b in payloads:
            try:
                frames.append(parse_one(b))
            except Exception as e:
                st.warning(f"Could not parse one file: {e}")
    if not frames:
        try:
            frames.append(parse_one(default_path))
        except Exception:
            return None
    master = pd.concat(frames, ignore_index=True)
    # De-duplicate by AGENT (keep first occurrence — Running Total has full Q1 data)
    master = master.drop_duplicates(subset=["AGENT"], keep="first")
    return master


# ══════════════════════════════════════════════════════════════════════════════
# 4 · SIDEBAR — UPLOAD + PROFILE TREE
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo / branding
    st.markdown(f"""
    <div style="padding:20px 0 16px">
      <div style="font-size:22px;font-weight:900;color:{PALETTE['text_primary']};
                  letter-spacing:-0.03em">
        📊 Q1 2026
      </div>
      <div style="font-size:11px;color:{PALETTE['text_muted']};
                  letter-spacing:0.09em;text-transform:uppercase;margin-top:2px">
        Executive Sales Intelligence
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f'<div style="height:1px;background:{PALETTE["border"]};margin:0 0 20px"></div>',
                unsafe_allow_html=True)

    # ── File upload ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="font-size:10px;font-weight:700;letter-spacing:0.1em;
                text-transform:uppercase;color:{PALETTE['text_muted']};
                margin-bottom:8px">Data Source</div>
    """, unsafe_allow_html=True)

    uploads = st.file_uploader(
        "Upload Q1 CSVs",
        type=["csv"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="Upload one or more Q1 report CSVs. Running Total auto-detected.",
    )

    DEFAULT_PATH = "GENERAL_Q1_REPORT__26_-_RUNNING_TOTAL_Q1__26.csv"
    payloads = [u.read() for u in uploads] if uploads else []

    with st.spinner("Loading data…"):
        df_raw = load_data(tuple(payloads), DEFAULT_PATH)

    if df_raw is None:
        st.error("No data found. Upload your Q1 CSV or place it in the same folder.")
        st.stop()

    n_agents  = len(df_raw)
    n_active  = (df_raw["STATUS"] == "ACTIVE").sum()
    n_regions = df_raw["REGION"].nunique()

    st.markdown(f"""
    <div style="background:{PALETTE['bg_subtle']};border:1px solid {PALETTE['border']};
                border-radius:10px;padding:12px 14px;margin:12px 0 20px">
      <div style="font-size:10px;color:{PALETTE['text_muted']};
                  text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px">
        Dataset loaded
      </div>
      <div style="color:{PALETTE['text_primary']};font-weight:700">
        {n_agents:,} agents · {n_regions} regions
      </div>
      <div style="font-size:11px;color:{PALETTE['accent_green']};margin-top:2px">
        {n_active:,} active ({n_active/n_agents*100:.0f}%)
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Profile Tree (cascading) ──────────────────────────────────────────────
    st.markdown(f"""
    <div style="font-size:10px;font-weight:700;letter-spacing:0.1em;
                text-transform:uppercase;color:{PALETTE['text_muted']};
                margin-bottom:12px;border-top:1px solid {PALETTE['border']};
                padding-top:16px">
      🌳 Profile Tree Drill-Down
    </div>
    """, unsafe_allow_html=True)

    df_scope = df_raw.copy()

    regions = sorted(df_scope["REGION"].dropna().unique())
    sel_region = st.selectbox("Region", ["◉  All Regions"] + regions,
                               format_func=lambda x: x.replace("◉  ", ""))
    if not sel_region.startswith("◉"):
        df_scope = df_scope[df_scope["REGION"] == sel_region]

    sm_opts = sorted(df_scope["SM"].dropna().unique())
    sel_sm = st.selectbox("Sales Manager", ["◉  All SMs"] + sm_opts,
                           format_func=lambda x: x.replace("◉  ", ""))
    if not sel_sm.startswith("◉"):
        df_scope = df_scope[df_scope["SM"] == sel_sm]

    mgr_opts = sorted(df_scope["MANAGER"].dropna().unique())
    sel_mgr = st.selectbox("Manager", ["◉  All Managers"] + mgr_opts,
                            format_func=lambda x: x.replace("◉  ", ""))
    if not sel_mgr.startswith("◉"):
        df_scope = df_scope[df_scope["MANAGER"] == sel_mgr]

    agent_opts = sorted(df_scope["AGENT"].dropna().unique())
    sel_agent = st.selectbox("Agent", ["◉  All Agents"] + agent_opts,
                              format_func=lambda x: x.replace("◉  ", ""))
    if not sel_agent.startswith("◉"):
        df_scope = df_scope[df_scope["AGENT"] == sel_agent]

    st.markdown(f"""
    <div style="font-size:11px;color:{PALETTE['text_muted']};
                margin-top:10px;padding-top:10px;
                border-top:1px solid {PALETTE['border']}">
      Viewing <b style="color:{PALETTE['text_primary']}">{len(df_scope):,}</b>
      of {n_agents:,} agents
    </div>
    """, unsafe_allow_html=True)

    # Status toggle
    st.markdown("")
    show_status = st.radio("Agent Status", ["All", "Active Only", "Inactive Only"],
                           horizontal=True)
    if show_status == "Active Only":
        df_scope = df_scope[df_scope["STATUS"] == "ACTIVE"]
    elif show_status == "Inactive Only":
        df_scope = df_scope[df_scope["STATUS"] == "INACTIVE"]

    # Scope label
    if not sel_agent.startswith("◉"):
        scope_label = f"Agent · {sel_agent}"
    elif not sel_mgr.startswith("◉"):
        scope_label = f"Manager · {sel_mgr}"
    elif not sel_sm.startswith("◉"):
        scope_label = f"SM · {sel_sm}"
    elif not sel_region.startswith("◉"):
        scope_label = f"Region · {sel_region}"
    else:
        scope_label = "All Regions — Q1 2026"


# ══════════════════════════════════════════════════════════════════════════════
# 5 · MAIN HEADER
# ══════════════════════════════════════════════════════════════════════════════
header_left, header_right = st.columns([3, 1])
with header_left:
    st.markdown(f"""
    <div style="padding:4px 0 6px">
      <div style="font-size:26px;font-weight:900;color:{PALETTE['text_primary']};
                  letter-spacing:-0.03em">
        Q1 2026 Sales Intelligence
      </div>
      <div style="font-size:14px;color:{PALETTE['text_muted']};margin-top:4px">
        Scope: <span style="color:{PALETTE['accent_blue']};font-weight:600">
        {scope_label}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with header_right:
    att = df_scope["SALES"].sum() / Q1_TARGET * 100
    att_color = PALETTE["accent_green"] if att >= 25 else (
        PALETTE["accent_amber"] if att >= 10 else PALETTE["accent_red"])
    st.markdown(f"""
    <div style="text-align:right;padding:6px 0">
      <div style="font-size:10px;text-transform:uppercase;letter-spacing:0.1em;
                  color:{PALETTE['text_muted']}">Q1 Target</div>
      <div style="font-size:20px;font-weight:800;color:{PALETTE['gold']}">
        {ngn(Q1_TARGET)}
      </div>
      <div style="font-size:13px;font-weight:700;color:{att_color}">
        {att:.2f}% Attained
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f'<div style="height:1px;background:{PALETTE["border"]};margin:8px 0 20px"></div>',
            unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 6 · AGENT SEARCH (always visible)
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("🔍  Agent Deep-Dive Search", expanded=False):
    search_col, _ = st.columns([2, 3])
    with search_col:
        search_query = st.text_input(
            "Search agent name",
            placeholder="e.g. EdoAliu, Lagos…",
            label_visibility="collapsed",
        )

    if search_query:
        mask = df_raw["AGENT"].str.contains(search_query, case=False, na=False)
        hits = df_raw[mask]
        if hits.empty:
            st.info("No agents found matching that query.")
        else:
            for _, row in hits.head(5).iterrows():
                status_badge = (
                    f'<span class="badge badge-green">ACTIVE</span>'
                    if row["STATUS"] == "ACTIVE"
                    else f'<span class="badge badge-red">INACTIVE</span>'
                )
                net_color = (PALETTE["accent_green"] if row["NET"] >= 0
                             else PALETTE["accent_red"])
                st.markdown(f"""
                <div class="agent-card" style="margin-bottom:12px">
                  <h3>{row['AGENT']} {status_badge}</h3>
                  <div class="sub">
                    {row['REGION']} › {row['SM']} › {row['MANAGER']}
                    &nbsp;·&nbsp; {row['ACTIVE DAYS']} active days
                  </div>
                  <div class="agent-grid">
                    <div class="agent-stat">
                      <div class="v">{ngn(row['SALES'])}</div>
                      <div class="l">Sales</div>
                    </div>
                    <div class="agent-stat">
                      <div class="v">{ngn(row['GGR'])}</div>
                      <div class="l">GGR</div>
                    </div>
                    <div class="agent-stat">
                      <div class="v">{ngn(row['NGR'])}</div>
                      <div class="l">NGR</div>
                    </div>
                    <div class="agent-stat">
                      <div class="v" style="color:{net_color}">{ngn(row['NET'])}</div>
                      <div class="l">Net Profit</div>
                    </div>
                    <div class="agent-stat">
                      <div class="v">{ngn(row['DEPOSITS'])}</div>
                      <div class="l">Deposits</div>
                    </div>
                    <div class="agent-stat">
                      <div class="v">{ngn(row['WITHDRAWALS'])}</div>
                      <div class="l">Withdrawals</div>
                    </div>
                  </div>
                  <!-- Product mini-bars -->
                  <div style="margin-top:16px">
                    {''.join([
                      f'<div style="margin-bottom:8px">'
                      f'<div style="display:flex;justify-content:space-between;'
                      f'font-size:11px;color:{PALETTE["text_muted"]};margin-bottom:3px">'
                      f'<span>{pname}</span><span>{ngn(row[sc])}</span></div>'
                      f'{progress_bar(row[sc], max(row["SB Sales"],row["LB Sales"],row["GB Sales"],row["GR Sales"],1), clr)}'
                      f'</div>'
                      for pname,(sc,_gc,clr) in PRODUCTS.items()
                      if sc in row and row[sc] > 0
                    ])}
                  </div>
                </div>
                """, unsafe_allow_html=True)

st.markdown("")


# ══════════════════════════════════════════════════════════════════════════════
# 7 · TABS
# ══════════════════════════════════════════════════════════════════════════════
tab_exec, tab_products, tab_quadrant, tab_leaderboard, tab_risk = st.tabs([
    "📋  Executive Scorecard",
    "🎮  Product Engine",
    "🎯  Profitability Quadrant",
    "🏆  Leaderboards",
    "⚠️  Risk Mitigation",
])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB A — EXECUTIVE SCORECARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_exec:

    # ── Aggregate KPIs ────────────────────────────────────────────────────────
    tot_sales  = df_scope["SALES"].sum()
    tot_ggr    = df_scope["GGR"].sum()
    tot_ngr    = df_scope["NGR"].sum()
    tot_net    = df_scope["NET"].sum()
    tot_deps   = df_scope["DEPOSITS"].sum()
    tot_wdraw  = df_scope["WITHDRAWALS"].sum()
    n_total    = len(df_scope)
    n_act      = (df_scope["STATUS"] == "ACTIVE").sum()
    n_inact    = n_total - n_act
    margin_pct = (tot_net / tot_sales * 100) if tot_sales > 0 else 0
    target_att = (tot_sales / Q1_TARGET * 100)
    comm_rate  = (df_scope["COMMISSION"].sum() / tot_sales * 100) if tot_sales > 0 else 0

    # KPI colour logic
    margin_cls = ("kpi-delta-good" if margin_pct >= 10
                  else "kpi-delta-warn" if margin_pct >= 0
                  else "kpi-delta-bad")
    att_cls    = ("kpi-delta-good" if target_att >= 25
                  else "kpi-delta-warn" if target_att >= 10
                  else "kpi-delta-bad")
    net_cls    = "kpi-delta-good" if tot_net >= 0 else "kpi-delta-bad"
    act_cls    = ("kpi-delta-good" if n_act / n_total > 0.3
                  else "kpi-delta-warn") if n_total > 0 else "kpi-delta-blue"

    # Row 1 — 4 primary KPIs
    st.markdown(sec("Primary Performance Indicators", "📌"), unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi_card(
        "Total Q1 Sales", ngn(tot_sales), "💰",
        f'<span class="{att_cls}">{target_att:.2f}% of ₦40.3B target</span>',
        PALETTE["accent_blue"],
    ), unsafe_allow_html=True)
    c2.markdown(kpi_card(
        "Gross Gaming Revenue", ngn(tot_ggr), "🎰",
        f'<span class="kpi-delta-blue">GGR/Sales: {pct(tot_ggr, tot_sales)}</span>',
        PALETTE["accent_teal"],
    ), unsafe_allow_html=True)
    c3.markdown(kpi_card(
        "Net Profit Margin", f"{margin_pct:.1f}%", "📈",
        f'<span class="{margin_cls}">Net: {ngn(tot_net)}</span>',
        PALETTE["accent_green"] if margin_pct >= 0 else PALETTE["accent_red"],
    ), unsafe_allow_html=True)
    c4.markdown(kpi_card(
        "Target Attainment", f"{target_att:.2f}%", "🎯",
        f'<span class="{att_cls}">Gap: {ngn(Q1_TARGET - tot_sales)}</span>',
        PALETTE["gold"],
    ), unsafe_allow_html=True)

    st.markdown("")

    # Row 2 — Secondary KPIs
    st.markdown(sec("Secondary Metrics", "📎"), unsafe_allow_html=True)
    d1, d2, d3, d4 = st.columns(4)
    d1.markdown(kpi_card(
        "Net Gaming Revenue", ngn(tot_ngr), "🏦",
        f'<span class="kpi-delta-blue">NGR/GGR: {pct(tot_ngr, tot_ggr)}</span>',
        PALETTE["chart_3"],
    ), unsafe_allow_html=True)
    d2.markdown(kpi_card(
        "Total Deposits", ngn(tot_deps), "⬇️",
        f'Withdrawals: {ngn(tot_wdraw)}',
        PALETTE["chart_4"],
    ), unsafe_allow_html=True)
    d3.markdown(kpi_card(
        "Commission Rate", f"{comm_rate:.1f}%", "🤝",
        f'Paid: {ngn(df_scope["COMMISSION"].sum())}',
        PALETTE["chart_5"],
    ), unsafe_allow_html=True)
    d4.markdown(kpi_card(
        "Agent Activity Rate", f"{n_act:,} / {n_total:,}", "👥",
        f'<span class="{act_cls}">{pct(n_act, n_total)} active</span>',
        PALETTE["accent_teal"],
    ), unsafe_allow_html=True)

    st.markdown("")

    # ── Target gauge + regional breakdown ─────────────────────────────────────
    st.markdown(sec("Target Progress & Regional Breakdown", "🗺️"), unsafe_allow_html=True)
    gauge_col, region_col = st.columns([1, 2])

    with gauge_col:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=tot_sales,
            delta={
                "reference": Q1_TARGET,
                "decreasing": {"color": PALETTE["accent_red"]},
                "increasing": {"color": PALETTE["accent_green"]},
                "valueformat": ",.0f",
            },
            number={"prefix": "₦", "valueformat": ",.0f",
                    "font": {"size": 22, "color": PALETTE["text_primary"]}},
            gauge={
                "axis": {
                    "range": [0, Q1_TARGET],
                    "tickvals": [0, Q1_TARGET*0.25, Q1_TARGET*0.5,
                                 Q1_TARGET*0.75, Q1_TARGET],
                    "ticktext": ["₦0", "25%", "50%", "75%", "Target"],
                    "tickfont": {"color": PALETTE["text_muted"], "size": 10},
                },
                "bar":  {"color": PALETTE["accent_blue"], "thickness": 0.25},
                "bgcolor": PALETTE["bg_card"],
                "bordercolor": PALETTE["border"],
                "steps": [
                    {"range": [0, Q1_TARGET*0.25], "color": "#0D1525"},
                    {"range": [Q1_TARGET*0.25, Q1_TARGET*0.5],  "color": "#0F1E35"},
                    {"range": [Q1_TARGET*0.5,  Q1_TARGET*0.75], "color": "#112540"},
                    {"range": [Q1_TARGET*0.75, Q1_TARGET],      "color": "#132C50"},
                ],
                "threshold": {
                    "line": {"color": PALETTE["gold"], "width": 3},
                    "thickness": 0.85,
                    "value": Q1_TARGET,
                },
            },
            title={"text": "Q1 Sales vs ₦40.3B Target",
                   "font": {"color": PALETTE["text_secondary"], "size": 13}},
        ))
        fig_g.update_layout(**PLOTLY_TEMPLATE["layout"], height=300,
                            margin=dict(l=20, r=20, t=60, b=10))
        st.plotly_chart(fig_g, use_container_width=True)

    with region_col:
        reg_df = (
            df_raw.groupby("REGION")
            .agg(Sales=("SALES", "sum"), Net=("NET", "sum"),
                 Active=("STATUS", lambda x: (x == "ACTIVE").sum()),
                 Total=("AGENT", "count"))
            .reset_index()
            .sort_values("Sales", ascending=False)
        )
        reg_df["Share"] = reg_df["Sales"] / reg_df["Sales"].sum() * 100
        fig_reg = go.Figure()
        fig_reg.add_trace(go.Bar(
            x=reg_df["REGION"], y=reg_df["Sales"],
            name="Sales", marker_color=PALETTE["accent_blue"],
            text=[ngn(v) for v in reg_df["Sales"]],
            textposition="outside", textfont=dict(size=11, color=PALETTE["text_primary"]),
            hovertemplate="<b>%{x}</b><br>Sales: ₦%{y:,.0f}<extra></extra>",
        ))
        fig_reg.add_trace(go.Bar(
            x=reg_df["REGION"], y=reg_df["Net"],
            name="Net Profit", marker_color=PALETTE["accent_green"],
            opacity=0.8,
            hovertemplate="<b>%{x}</b><br>Net: ₦%{y:,.0f}<extra></extra>",
        ))
        apply_theme(fig_reg, 300)
        fig_reg.update_layout(
            barmode="group", title="Regional Sales vs Net Profit",
            legend=dict(orientation="h", y=1.12),
            yaxis_tickformat=",.0s",
        )
        st.plotly_chart(fig_reg, use_container_width=True)

    # ── Activity funnel ───────────────────────────────────────────────────────
    st.markdown(sec("Agent Activity Funnel", "⚡"), unsafe_allow_html=True)
    act_df = (
        df_scope.groupby("REGION")
        .agg(total=("AGENT","count"),
             active=("STATUS", lambda x: (x=="ACTIVE").sum()))
        .reset_index()
    )
    act_df["inactive"] = act_df["total"] - act_df["active"]
    act_df["rate"] = act_df["active"] / act_df["total"] * 100

    fig_act = go.Figure()
    fig_act.add_trace(go.Bar(x=act_df["REGION"], y=act_df["active"],
                             name="Active", marker_color=PALETTE["accent_green"],
                             hovertemplate="%{x}: %{y} active<extra></extra>"))
    fig_act.add_trace(go.Bar(x=act_df["REGION"], y=act_df["inactive"],
                             name="Inactive", marker_color=PALETTE["accent_red"],
                             opacity=0.6,
                             hovertemplate="%{x}: %{y} inactive<extra></extra>"))
    for _, r in act_df.iterrows():
        fig_act.add_annotation(
            x=r["REGION"], y=r["total"],
            text=f"{r['rate']:.0f}%",
            showarrow=False, yshift=10,
            font=dict(color=PALETTE["text_primary"], size=11, family="Inter"),
        )
    apply_theme(fig_act, 300)
    fig_act.update_layout(barmode="stack", title="Active vs Inactive Agents by Region",
                          yaxis_title="Agent Count")
    st.plotly_chart(fig_act, use_container_width=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB B — PRODUCT PERFORMANCE ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_products:
    st.markdown(sec("Product Contribution Overview", "🎮"), unsafe_allow_html=True)

    prod_totals = {
        p: {"Sales": df_scope[sc].sum(), "GGR": df_scope[gc].sum(), "Color": cl}
        for p, (sc, gc, cl) in PRODUCTS.items()
        if sc in df_scope.columns
    }
    prod_df = pd.DataFrame(prod_totals).T.reset_index()
    prod_df.columns = ["Product", "Sales", "GGR", "Color"]
    prod_df["Sales_pct"] = prod_df["Sales"] / prod_df["Sales"].sum() * 100

    # KPI mini-row for products
    p_cols = st.columns(4)
    for i, (pname, row) in enumerate(prod_df.iterrows()):
        pname = prod_df.iloc[i]["Product"]
        color = prod_df.iloc[i]["Color"]
        share = prod_df.iloc[i]["Sales_pct"]
        sales  = prod_df.iloc[i]["Sales"]
        p_cols[i].markdown(kpi_card(
            pname, ngn(sales), "🎮",
            f'<span style="color:{color}">{share:.1f}% of product sales</span>',
            color,
        ), unsafe_allow_html=True)

    st.markdown("")
    chart_l, chart_r = st.columns([3, 2])

    with chart_l:
        # Stacked bar by Region × Product
        region_prod = {}
        for pname, (sc, gc, cl) in PRODUCTS.items():
            if sc in df_scope.columns:
                region_prod[pname] = df_scope.groupby("REGION")[sc].sum()

        rp_df = pd.DataFrame(region_prod).fillna(0).reset_index()
        rp_df_melt = rp_df.melt(id_vars="REGION", var_name="Product", value_name="Sales")
        color_map = {p: PRODUCTS[p][2] for p in PRODUCTS}

        fig_stack = px.bar(
            rp_df_melt, x="REGION", y="Sales", color="Product",
            color_discrete_map=color_map,
            title="Stacked Product Mix by Region",
            barmode="stack",
            text_auto=False,
            hover_data={"Sales": ":,.0f"},
        )
        apply_theme(fig_stack, 400)
        fig_stack.update_layout(
            yaxis_tickformat=",.0s", yaxis_title="Sales (₦)",
            legend=dict(orientation="h", y=1.08),
        )
        st.plotly_chart(fig_stack, use_container_width=True)

    with chart_r:
        # Donut
        fig_donut = go.Figure(go.Pie(
            labels=prod_df["Product"],
            values=prod_df["Sales"],
            hole=0.62,
            marker=dict(colors=prod_df["Color"].tolist(),
                        line=dict(color=PALETTE["bg_main"], width=3)),
            textinfo="percent+label",
            textfont=dict(size=12, color=PALETTE["text_primary"]),
            hovertemplate="<b>%{label}</b><br>₦%{value:,.0f}<br>%{percent}<extra></extra>",
        ))
        fig_donut.add_annotation(
            text=f"<b>{ngn(prod_df['Sales'].sum())}</b><br><span style='font-size:9px'>Total Sales</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color=PALETTE["text_primary"]),
        )
        apply_theme(fig_donut, 400)
        fig_donut.update_layout(
            title="Overall Product Mix",
            showlegend=False,
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # Product × SM heatmap
    st.markdown(sec("Product Sales Intensity by SM", "🌡️"), unsafe_allow_html=True)
    heat_data = {}
    for pname, (sc, _, _) in PRODUCTS.items():
        if sc in df_scope.columns:
            heat_data[pname] = df_scope.groupby("SM")[sc].sum()

    heat_df = pd.DataFrame(heat_data).fillna(0)
    heat_pct = heat_df.div(heat_df.sum(axis=1), axis=0) * 100

    fig_heat = px.imshow(
        heat_pct,
        text_auto=".0f",
        color_continuous_scale=[[0, "#0D1525"], [0.5, "#1E3A6E"], [1, "#3B7DD8"]],
        aspect="auto",
        title="Product Share (%) per SM — darker = higher concentration",
    )
    fig_heat.update_traces(texttemplate="%{z:.0f}%",
                           textfont=dict(color=PALETTE["text_primary"], size=11))
    apply_theme(fig_heat, 360)
    fig_heat.update_coloraxes(colorbar_tickfont_color=PALETTE["text_muted"])
    st.plotly_chart(fig_heat, use_container_width=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB C — PROFITABILITY QUADRANT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_quadrant:
    st.markdown(sec("Scatter: Sales Volume vs Net Profit", "🎯"), unsafe_allow_html=True)

    active_q = df_scope[df_scope["STATUS"] == "ACTIVE"].copy()
    if active_q.empty:
        st.info("No active agents in current scope.")
    else:
        med_sales = active_q["SALES"].median()
        med_net   = active_q["NET"].median()

        def quadrant(row):
            if row["SALES"] >= med_sales and row["NET"] >= med_net:
                return "⭐ Star Performers"
            elif row["SALES"] >= med_sales and row["NET"] < med_net:
                return "⚡ High Volume / Low Profit"
            elif row["SALES"] < med_sales and row["NET"] >= med_net:
                return "💎 Efficient Niche"
            else:
                return "⚠️ Underperformers"

        active_q["Quadrant"] = active_q.apply(quadrant, axis=1)

        q_colors = {
            "⭐ Star Performers":         PALETTE["accent_green"],
            "⚡ High Volume / Low Profit": PALETTE["accent_amber"],
            "💎 Efficient Niche":          PALETTE["accent_blue"],
            "⚠️ Underperformers":          PALETTE["accent_red"],
        }

        fig_scatter = px.scatter(
            active_q,
            x="SALES", y="NET",
            color="Quadrant",
            color_discrete_map=q_colors,
            size="GGR",
            size_max=35,
            hover_data={"AGENT": True, "REGION": True, "SM": True,
                        "SALES": ":,.0f", "NET": ":,.0f", "GGR": ":,.0f"},
            title="Profitability Quadrant — Sales vs Net Profit (bubble size = GGR)",
            labels={"SALES": "Total Sales (₦)", "NET": "Net Profit (₦)"},
        )

        # Quadrant dividers
        fig_scatter.add_vline(x=med_sales, line_dash="dash",
                              line_color=PALETTE["border_bright"], line_width=1.5,
                              annotation_text=f"Median Sales {ngn(med_sales)}",
                              annotation_font_color=PALETTE["text_muted"],
                              annotation_position="top right")
        fig_scatter.add_hline(y=med_net, line_dash="dash",
                              line_color=PALETTE["border_bright"], line_width=1.5,
                              annotation_text=f"Median Net {ngn(med_net)}",
                              annotation_font_color=PALETTE["text_muted"],
                              annotation_position="top right")

        # Quadrant labels
        x_max = active_q["SALES"].max()
        y_max = active_q["NET"].max()
        y_min = active_q["NET"].min()

        for label, xpos, ypos in [
            ("⭐ STARS",           x_max * 0.85, y_max * 0.9),
            ("⚡ HIGH VOL",        x_max * 0.85, y_min * 0.8),
            ("💎 EFFICIENT",       med_sales*0.05, y_max * 0.9),
            ("⚠️ UNDERPERF",       med_sales*0.05, y_min * 0.8),
        ]:
            fig_scatter.add_annotation(
                x=xpos, y=ypos, text=label,
                showarrow=False,
                font=dict(color=PALETTE["text_muted"], size=10),
                opacity=0.6,
            )

        apply_theme(fig_scatter, 520)
        fig_scatter.update_layout(
            xaxis_tickformat=",.0s", yaxis_tickformat=",.0s",
            legend=dict(orientation="h", y=1.08),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Quadrant summary table
        st.markdown(sec("Quadrant Summary", "📋"), unsafe_allow_html=True)
        q_summary = (
            active_q.groupby("Quadrant")
            .agg(Agents=("AGENT","count"),
                 TotalSales=("SALES","sum"),
                 TotalNet=("NET","sum"),
                 AvgSales=("SALES","mean"),
                 AvgNet=("NET","mean"))
            .reset_index()
            .sort_values("TotalNet", ascending=False)
        )
        for col in ["TotalSales","TotalNet","AvgSales","AvgNet"]:
            q_summary[col] = q_summary[col].apply(ngn)
        q_summary.columns = ["Quadrant","# Agents","Total Sales","Total Net",
                              "Avg Sales","Avg Net"]
        st.dataframe(q_summary, use_container_width=True, hide_index=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB D — LEADERBOARDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_leaderboard:
    active_lb = df_scope[df_scope["STATUS"] == "ACTIVE"]

    top5    = active_lb.nlargest(5,  "NET")
    bottom5 = active_lb.nsmallest(5, "NET")

    top_col, bot_col = st.columns(2)

    with top_col:
        st.markdown(sec("Top 5 Agents · Net Profit", "🏆"), unsafe_allow_html=True)
        for i, (_, row) in enumerate(top5.iterrows(), 1):
            cls, icon = rank_medal(i)
            net_clr = PALETTE["accent_green"] if row["NET"] >= 0 else PALETTE["accent_red"]
            st.markdown(f"""
            <div class="leader-row">
              <div class="leader-rank {cls}">{icon}</div>
              <div class="leader-info">
                <div class="leader-name">{row['AGENT']}</div>
                <div class="leader-meta">{row['REGION']} · {row['SM']} · {row['MANAGER']}</div>
                <div class="leader-meta">Sales: {ngn(row['SALES'])} &nbsp;|&nbsp;
                  Active: {row['ACTIVE DAYS']}d</div>
              </div>
              <div class="leader-value" style="color:{net_clr}">{ngn(row['NET'])}</div>
            </div>
            """, unsafe_allow_html=True)

    with bot_col:
        st.markdown(sec("Bottom 5 Agents · Net Profit", "📉"), unsafe_allow_html=True)
        for i, (_, row) in enumerate(bottom5.iterrows(), 1):
            # Diagnose root cause
            if row["WITHDRAWALS"] > row["SALES"] * 0.5:
                badge_html = '<span class="badge badge-red">High Withdrawals</span>'
            elif row["EXPENSES"] > abs(row["NET"]) * 0.3:
                badge_html = '<span class="badge badge-amber">High Expenses</span>'
            elif row["GGR"] < 0:
                badge_html = '<span class="badge badge-red">Negative GGR</span>'
            else:
                badge_html = '<span class="badge badge-blue">Low Turnover</span>'

            st.markdown(f"""
            <div class="leader-row">
              <div class="leader-rank">#{i}</div>
              <div class="leader-info">
                <div class="leader-name">{row['AGENT']} {badge_html}</div>
                <div class="leader-meta">{row['REGION']} · {row['SM']} · {row['MANAGER']}</div>
                <div class="leader-meta">Sales: {ngn(row['SALES'])} &nbsp;|&nbsp;
                  W/D: {ngn(row['WITHDRAWALS'])}</div>
              </div>
              <div class="leader-value neg">{ngn(row['NET'])}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── SM Ranking ─────────────────────────────────────────────────────────────
    st.markdown(sec("Sales Manager Ranking", "👔"), unsafe_allow_html=True)
    sm_rank = (
        df_scope.groupby(["REGION","SM"])
        .agg(Agents=("AGENT","count"),
             Active=("STATUS", lambda x: (x=="ACTIVE").sum()),
             Sales=("SALES","sum"),
             GGR=("GGR","sum"),
             Net=("NET","sum"))
        .reset_index()
        .sort_values("Net", ascending=False)
        .reset_index(drop=True)
    )
    sm_rank.insert(0, "Rank", range(1, len(sm_rank)+1))
    sm_rank["Activity"] = (sm_rank["Active"]/sm_rank["Agents"]*100).round(1).astype(str)+"%"
    sm_rank["Sales"] = sm_rank["Sales"].apply(ngn)
    sm_rank["GGR"]   = sm_rank["GGR"].apply(ngn)
    sm_rank["Net"]   = sm_rank["Net"].apply(ngn)
    sm_rank.drop(columns=["Active"], inplace=True)
    st.dataframe(sm_rank, use_container_width=True, hide_index=True)

    # ── Top 10 by Sales (all scopes) ──────────────────────────────────────────
    st.markdown(sec("Top 10 Agents by Sales Volume", "💰"), unsafe_allow_html=True)
    top10_sales = df_scope.nlargest(10, "SALES")[
        ["AGENT","REGION","SM","STATUS","SALES","GGR","NGR","NET","ACTIVE DAYS"]
    ].copy()
    for col in ["SALES","GGR","NGR","NET"]:
        top10_sales[col] = top10_sales[col].apply(ngn)
    st.dataframe(top10_sales.reset_index(drop=True), use_container_width=True, hide_index=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB E — RISK MITIGATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_risk:

    inactive_df = df_scope[df_scope["STATUS"] == "INACTIVE"].copy()
    high_wd_df  = df_scope[
        (df_scope["STATUS"] == "ACTIVE") &
        (df_scope["WITHDRAWAL_RATE"] > 70)
    ].copy()

    # ── Risk KPI row ──────────────────────────────────────────────────────────
    st.markdown(sec("Risk Overview", "⚠️"), unsafe_allow_html=True)
    lost_rev   = inactive_df["SALES"].sum()
    avg_active = df_scope[df_scope["STATUS"]=="ACTIVE"]["SALES"].mean() if n_act > 0 else 0
    proj_recov = avg_active * len(inactive_df)
    wd_exposure = high_wd_df["WITHDRAWALS"].sum()

    r1, r2, r3, r4 = st.columns(4)
    r1.markdown(kpi_card(
        "Inactive Agents", f"{len(inactive_df):,}", "💤",
        f'{pct(len(inactive_df), n_total)} of scope',
        PALETTE["accent_red"],
    ), unsafe_allow_html=True)
    r2.markdown(kpi_card(
        "Lost Revenue (Inactive)", ngn(lost_rev), "📉",
        "Last-known Q1 sales from inactive agents",
        PALETTE["accent_amber"],
    ), unsafe_allow_html=True)
    r3.markdown(kpi_card(
        "Recovery Potential", ngn(proj_recov), "🔄",
        "If inactives matched active avg sales",
        PALETTE["accent_green"],
    ), unsafe_allow_html=True)
    r4.markdown(kpi_card(
        "High W/D Exposure", ngn(wd_exposure), "🚨",
        f"{len(high_wd_df)} agents with >70% withdrawal rate",
        PALETTE["accent_red"],
    ), unsafe_allow_html=True)

    st.markdown("")

    # ── Inactive tab ──────────────────────────────────────────────────────────
    risk_tab1, risk_tab2 = st.tabs(["💤  Inactive Agents", "🚨  High Withdrawal Agents"])

    with risk_tab1:
        # Priority score: sales per active day — the higher, the more worth re-engaging
        inactive_df["Re-Engage Score"] = np.where(
            inactive_df["ACTIVE DAYS"] > 0,
            inactive_df["SALES"] / inactive_df["ACTIVE DAYS"],
            0,
        ).round(0)
        inactive_df["Priority"] = pd.qcut(
            inactive_df["Re-Engage Score"].rank(method="first"),
            q=3, labels=["Low 🟢", "Medium 🟡", "High 🔴"]
        )

        # Charts
        ia1, ia2 = st.columns(2)
        with ia1:
            fig_inactive_reg = px.bar(
                inactive_df.groupby("REGION").size().reset_index(name="Count")
                .sort_values("Count", ascending=True),
                x="Count", y="REGION", orientation="h",
                color="Count",
                color_continuous_scale=[[0,"#132C50"],[1,"#EF4444"]],
                title="Inactive Agents by Region",
            )
            apply_theme(fig_inactive_reg, 280)
            fig_inactive_reg.update_layout(showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_inactive_reg, use_container_width=True)

        with ia2:
            fig_days = px.histogram(
                inactive_df[inactive_df["ACTIVE DAYS"] > 0],
                x="ACTIVE DAYS", nbins=25,
                color="REGION",
                title="Active-Days Distribution (Inactive Agents)",
                barmode="stack",
            )
            apply_theme(fig_days, 280)
            fig_days.update_layout(
                legend=dict(orientation="h", y=1.1, font_size=10),
                xaxis_title="Days Active Before Churning",
            )
            st.plotly_chart(fig_days, use_container_width=True)

        # Top re-engage targets
        st.markdown(sec("Priority Re-Engagement List", "🎯"), unsafe_allow_html=True)
        top_re = (
            inactive_df
            .nlargest(30, "Re-Engage Score")
            [["AGENT","MANAGER","SM","REGION","ACTIVE DAYS","SALES","NET",
              "Re-Engage Score","Priority"]]
            .copy()
        )
        top_re["SALES"] = top_re["SALES"].apply(ngn)
        top_re["NET"]   = top_re["NET"].apply(ngn)
        top_re["Re-Engage Score"] = top_re["Re-Engage Score"].apply(
            lambda x: f"₦{x:,.0f}/day"
        )
        st.dataframe(top_re.reset_index(drop=True), use_container_width=True, hide_index=True)

    with risk_tab2:
        if high_wd_df.empty:
            st.info("No active agents with withdrawal rate above 70% in current scope.")
        else:
            hwd1, hwd2 = st.columns(2)
            with hwd1:
                fig_wd = px.scatter(
                    high_wd_df,
                    x="DEPOSITS", y="WITHDRAWALS",
                    color="WITHDRAWAL_RATE",
                    size="SALES",
                    size_max=30,
                    color_continuous_scale=[[0,"#F59E0B"],[0.5,"#EF4444"],[1,"#7F1D1D"]],
                    hover_data={"AGENT": True, "REGION": True,
                                "DEPOSITS": ":,.0f", "WITHDRAWALS": ":,.0f",
                                "WITHDRAWAL_RATE": ":.1f"},
                    title="Deposits vs Withdrawals (size = Sales)",
                    labels={"DEPOSITS": "Deposits (₦)", "WITHDRAWALS": "Withdrawals (₦)",
                            "WITHDRAWAL_RATE": "W/D Rate (%)"},
                )
                apply_theme(fig_wd, 340)
                fig_wd.update_coloraxes(
                    colorbar_tickfont_color=PALETTE["text_muted"],
                    colorbar_title_font_color=PALETTE["text_muted"],
                )
                st.plotly_chart(fig_wd, use_container_width=True)

            with hwd2:
                wd_reg = (
                    high_wd_df.groupby("REGION")
                    .agg(Count=("AGENT","count"),
                         TotalWD=("WITHDRAWALS","sum"),
                         AvgRate=("WITHDRAWAL_RATE","mean"))
                    .reset_index()
                    .sort_values("TotalWD", ascending=True)
                )
                fig_wd_bar = px.bar(
                    wd_reg, x="TotalWD", y="REGION", orientation="h",
                    color="AvgRate",
                    color_continuous_scale=[[0,"#F59E0B"],[1,"#EF4444"]],
                    title="W/D Exposure by Region",
                    labels={"TotalWD": "Total Withdrawals (₦)", "AvgRate": "Avg Rate %"},
                    text=[ngn(v) for v in wd_reg["TotalWD"]],
                )
                apply_theme(fig_wd_bar, 340)
                fig_wd_bar.update_traces(textposition="outside",
                                        textfont_color=PALETTE["text_primary"])
                fig_wd_bar.update_coloraxes(
                    colorbar_tickfont_color=PALETTE["text_muted"],
                    colorbar_title_font_color=PALETTE["text_muted"],
                )
                st.plotly_chart(fig_wd_bar, use_container_width=True)

            st.markdown(sec("High Withdrawal Agent Details", "📋"), unsafe_allow_html=True)
            wd_detail = high_wd_df.nlargest(20, "WITHDRAWAL_RATE")[
                ["AGENT","REGION","SM","MANAGER","SALES","DEPOSITS",
                 "WITHDRAWALS","WITHDRAWAL_RATE","NET"]
            ].copy()
            wd_detail["SALES"]       = wd_detail["SALES"].apply(ngn)
            wd_detail["DEPOSITS"]    = wd_detail["DEPOSITS"].apply(ngn)
            wd_detail["WITHDRAWALS"] = wd_detail["WITHDRAWALS"].apply(ngn)
            wd_detail["NET"]         = wd_detail["NET"].apply(ngn)
            wd_detail["WITHDRAWAL_RATE"] = wd_detail["WITHDRAWAL_RATE"].apply(
                lambda x: f"{x:.1f}%"
            )
            wd_detail.columns = ["Agent","Region","SM","Manager","Sales",
                                 "Deposits","Withdrawals","W/D Rate","Net"]
            st.dataframe(wd_detail.reset_index(drop=True),
                         use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div style="height:1px;background:{PALETTE['border']};margin:32px 0 16px"></div>
<div style="display:flex;justify-content:space-between;align-items:center;
            padding-bottom:24px">
  <div style="font-size:12px;color:{PALETTE['text_muted']}">
    Q1 2026 Executive Sales Dashboard &nbsp;·&nbsp; Powered by Streamlit &amp; Plotly
  </div>
  <div style="font-size:11px;color:{PALETTE['text_muted']}">
    {len(df_raw):,} agents loaded &nbsp;·&nbsp;
    Target: <span style="color:{PALETTE['gold']}">₦{Q1_TARGET:,.2f}</span>
  </div>
</div>
""", unsafe_allow_html=True)
