import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re
import io

# 1. PAGE CONFIG & THEME
st.set_page_config(page_title="iGaming Retail OS | Executive View", layout="wide", page_icon="🏦")

# Industrial Design System
PALETTE = {
    "bg": "#070B14", "card": "#0D1525", "border": "#1E2D45",
    "text": "#E8EDF5", "muted": "#7A8BAD", "accent": "#3B7DD8",
    "green": "#22C55E", "red": "#EF4444", "amber": "#F59E0B"
}

st.markdown(f"""
    <style>
    .stApp {{ background-color: {PALETTE['bg']}; color: {PALETTE['text']}; }}
    [data-testid="stMetricValue"] {{ color: {PALETTE['accent']}; font-weight: 800; }}
    .kpi-card {{
        background: {PALETTE['card']}; border: 1px solid {PALETTE['border']};
        border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 15px;
    }}
    .stTabs [data-baseweb="tab-list"] {{ background-color: {PALETTE['card']}; border-radius: 10px; padding: 5px; }}
    </style>
""", unsafe_allow_html=True)

# 2. ROBUST DATA CLEANING ENGINE
def clean_currency(val):
    if pd.isna(val) or str(val).strip() == "": return 0.0
    # Handle symbols, commas, and negative signs like -₦60.00 or (₦60.00)
    s = str(val).replace('₦', '').replace(',', '').replace(' ', '')
    s = re.sub(r'\(', '-', s).replace(')', '')
    try: return float(s)
    except: return 0.0

def ngn(v):
    if pd.isna(v) or v == 0: return "₦0"
    neg = "-" if v < 0 else ""
    v = abs(v)
    if v >= 1e9: return f"{neg}₦{v/1e9:,.2f}B"
    if v >= 1e6: return f"{neg}₦{v/1e6:,.1f}M"
    return f"{neg}₦{v:,.0f}"

# 3. ADVANCED DATA INGESTION
@st.cache_data
def process_igaming_data(uploaded_files):
    if not uploaded_files: return None
    
    all_frames = []
    for f in uploaded_files:
        # Check if Excel or CSV
        if f.name.endswith('.xlsx'):
            return pd.read_excel(f, sheet_name=None) # Returns a dict of dataframes
        
        # Robust CSV Skip logic (detects Running Total vs Others)
        header_peek = pd.read_csv(f, nrows=10, header=None)
        skip = 9 if "TARGET" in str(header_peek.iloc[0,0]) else 4
        f.seek(0)
        df = pd.read_csv(f, skiprows=skip)
        
        # Clean Columns
        df.columns = [c.strip().upper() for c in df.columns]
        # Remove regional 'Total' rows to prevent double counting
        if 'AGENT' in df.columns:
            df = df[df['AGENT'].notna() & ~df['AGENT'].str.contains('Total', case=False, na=False)]
        
        all_frames.append(df)
    
    master = pd.concat(all_frames, ignore_index=True)
    
    # Critical Numeric Transformation
    fin_cols = ['SALES', 'GGR', 'NGR', 'NET', 'COMMISSION', 'DEPOSITS', 'WITHDRAWALS', 'EXPENSES',
                'SB SALES', 'SB GGR', 'LB SALES', 'LB GGR', 'GB SALES', 'GB GGR', 'GR SALES', 'GR GGR']
    
    for col in fin_cols:
        if col in master.columns:
            master[col] = master[col].apply(clean_currency)
    
    if 'ACTIVE DAYS' in master.columns:
        master['ACTIVE DAYS'] = pd.to_numeric(master['ACTIVE DAYS'], errors='coerce').fillna(0)
        
    return {"Sales_Data": master}

# 4. SIDEBAR & HIERARCHY FILTERS
with st.sidebar:
    st.title("🏦 Retail OS Login")
    user_role = st.selectbox("Role", ["Super Admin", "Regional Dir", "SM", "Manager"])
    
    st.markdown("---")
    st.subheader("📁 Database Sync")
    files = st.file_uploader("Upload Q1 CSVs or Master Workbook", accept_multiple_files=True)
    db = process_igaming_data(files)

if not db:
    st.info("👋 Welcome. Please upload the Q1 Sales CSV to initialize the Intelligence Engine.")
    st.stop()

# Get Master Sales DF
sales_df = db.get('Sales_Data', pd.DataFrame())

# Profile Tree Hierarchy Selection
st.sidebar.markdown("### 🌳 Profile Tree Filter")
regions = sorted(sales_df['REGION'].unique()) if 'REGION' in sales_df.columns else []
sel_region = st.sidebar.selectbox("Select Region", ["ALL"] + regions)

filtered_df = sales_df.copy()
if sel_region != "ALL":
    filtered_df = filtered_df[filtered_df['REGION'] == sel_region]
    sms = sorted(filtered_df['SM'].unique())
    sel_sm = st.sidebar.selectbox("Select SM", ["ALL"] + sms)
    if sel_sm != "ALL":
        filtered_df = filtered_df[filtered_df['SM'] == sel_sm]
        mgrs = sorted(filtered_df['MANAGER'].unique())
        sel_mgr = st.sidebar.selectbox("Select Manager", ["ALL"] + mgrs)
        if sel_mgr != "ALL":
            filtered_df = filtered_df[filtered_df['MANAGER'] == sel_mgr]

# 5. MAIN INTERFACE
st.title("🚀 iGaming Retail Management OS")
st.markdown(f"**Live Scope:** {sel_region} Hierarchy | **Agents in View:** {len(filtered_df)}")

# Tabs for Holistic Management
tab_sales, tab_products, tab_lifecycle, tab_crm, tab_logistics = st.tabs([
    "📈 Sales Performance", "🎮 Product Mix", "🕵️ Agent Lifecycle", "📞 CRM Activity", "🚚 Field Ops"
])

# MODULE 1: SALES & EXECUTIVE KPIs
with tab_sales:
    target = 40319855100
    actual = filtered_df['SALES'].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sales", ngn(actual), f"{(actual/target)*100:.1f}% of Target")
    c2.metric("GGR (Gross)", ngn(filtered_df['GGR'].sum()))
    c3.metric("Net Profit", ngn(filtered_df['NET'].sum()))
    c4.metric("Operations Expense", ngn(filtered_df['EXPENSES'].sum()), delta_color="inverse")

    # Sales vs Profit Scatter
    st.subheader("🎯 Profitability Quadrant")
    plot_df = filtered_df[filtered_df['SALES'] > 0].copy()
    plot_df['Size'] = plot_df['SALES'].clip(lower=1)
    fig_q = px.scatter(plot_df, x="SALES", y="NET", size="Size", hover_name="AGENT",
                      color="SM" if sel_region != "ALL" else "REGION",
                      template="plotly_dark", title="Sales Volume vs. Net Profitability")
    st.plotly_chart(fig_q, use_container_width=True)

# MODULE 2: PRODUCT ENGINE (SB, LB, GB, GR)
with tab_products:
    st.header("Product Performance Breakdown")
    prod_metrics = []
    for p in ['SB', 'LB', 'GB', 'GR']:
        s_col, g_col = f'{p} SALES', f'{p} GGR'
        if s_col in filtered_df.columns:
            prod_metrics.append({"Product": p, "Sales": filtered_df[s_col].sum(), "GGR": filtered_df[g_col].sum()})
    
    p_df = pd.DataFrame(prod_metrics)
    
    col_l, col_r = st.columns(2)
    fig_pie = px.pie(p_df, values='Sales', names='Product', hole=0.5, title="Sales Contribution by Product")
    col_l.plotly_chart(fig_pie, use_container_width=True)
    
    fig_bar = px.bar(p_df, x='Product', y='Sales', color='Product', title="Total Sales per Product Category")
    col_r.plotly_chart(fig_bar, use_container_width=True)

# MODULE 3: AGENT LIFECYCLE & RISK
with tab_lifecycle:
    st.header("Retention & Risk Analysis")
    if 'STATUS' in filtered_df.columns:
        inactive = filtered_df[filtered_df['STATUS'] == 'INACTIVE']
        st.error(f"⚠️ {len(inactive)} Inactive Agents found in current tree.")
        
        st.subheader("Top 10 High-Value Lost Agents (by Last Sales)")
        st.table(inactive.nlargest(10, 'SALES')[['AGENT', 'MANAGER', 'SALES', 'ACTIVE DAYS']])

# MODULE 4 & 5: CRM & LOGISTICS (Placeholders or from Workbook)
with tab_crm:
    st.header("CRM Call Intelligence")
    st.info("Connect 'CRM_Activity_Log' sheet to view real-time call performance and assigned tasks.")
    # If the sheet exists in db, display it
    if "CRM_Activity_Log" in db:
        st.dataframe(filter_df(db["CRM_Activity_Log"]))

with tab_logistics:
    st.header("Field Visit & Logistics Management")
    st.info("Logistics tracking requires the 'Logistics_Visits' sheet from your Retail OS Workbook.")
    if "Logistics_Visits" in db:
        st.dataframe(filter_df(db["Logistics_Visits"]))
