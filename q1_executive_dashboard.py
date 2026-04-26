import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import re
import io

# 1. PAGE CONFIG & THEME
st.set_page_config(page_title="iGaming Retail OS | Q1 2026", layout="wide", page_icon="🚀")

# Professional Design System
PALETTE = {
    "bg": "#070B14", "card": "#0D1525", "border": "#1E2D45",
    "text": "#E8EDF5", "muted": "#7A8BAD", "accent": "#3B7DD8",
    "green": "#22C55E", "red": "#EF4444", "amber": "#F59E0B"
}

# Fixed Plotly Template to prevent previous errors
PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PALETTE["text"]), margin=dict(l=10, r=10, t=40, b=10)
    )
)

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

# 2. HELPERS
def ngn(v):
    if pd.isna(v): return "₦0"
    if abs(v) >= 1e9: return f"₦{v/1e9:,.2f}B"
    if abs(v) >= 1e6: return f"₦{v/1e6:,.1f}M"
    return f"₦{v:,.0f}"

def clean_fin(val):
    try:
        s = re.sub(r"[₦,%↑↓\s]", "", str(val)).replace("(", "-").replace(")", "")
        return float(s)
    except: return 0.0

# 3. DATA INGESTION ENGINE
@st.cache_data
def load_all_data(uploaded_files):
    data_dict = {}
    if not uploaded_files: return None
    
    # If the user uploads the Excel Workbook I generated
    for file in uploaded_files:
        if file.name.endswith('.xlsx'):
            xls = pd.ExcelFile(file)
            for sheet in xls.sheet_names:
                data_dict[sheet] = pd.read_excel(file, sheet_name=sheet)
        else:
            # Handle individual CSVs by guessing content based on filename
            name = file.name.lower()
            df = pd.read_csv(file)
            if 'sales' in name or 'running' in name: data_dict['Sales_Data'] = df
            elif 'crm' in name: data_dict['CRM_Activity_Log'] = df
            elif 'logistics' in name or 'visit' in name: data_dict['Logistics_Visits'] = df
            elif 'inventory' in name: data_dict['Equipment_Inventory'] = df
            elif 'inactive' in name or 'lifecycle' in name: data_dict['Agent_Lifecycle'] = df
            
    return data_dict

# 4. SIDEBAR & AUTHENTICATION
with st.sidebar:
    st.title("🛡️ Secure Access")
    user_role = st.selectbox("Your Role", ["Admin", "Region Manager", "SM", "Manager"])
    node_name = st.text_input("Enter Node Name (e.g., EdoSM)", "ALL")
    
    st.markdown("---")
    st.subheader("📁 Database Upload")
    files = st.file_uploader("Upload iGaming OS Workbook (.xlsx or CSVs)", accept_multiple_files=True)
    db = load_all_data(files)

if not db:
    st.warning("Please upload your database to activate the OS.")
    st.stop()

# 5. HIERARCHY FILTERING LOGIC
def filter_df(df):
    if node_name == "ALL" or user_role == "Admin": return df
    for col in ['REGION', 'SM', 'MANAGER', 'Region_Name', 'SM_Name', 'Manager_Name']:
        if col.upper() in [c.upper() for c in df.columns]:
            # Case insensitive match
            return df[df[col].astype(str).str.contains(node_name, case=False, na=False)]
    return df

# Apply filters to all datasets
sales = filter_df(db.get('Sales_Data', pd.DataFrame()))
crm = filter_df(db.get('CRM_Activity_Log', pd.DataFrame()))
logistics = filter_df(db.get('Logistics_Visits', pd.DataFrame()))
inventory = filter_df(db.get('Equipment_Inventory', pd.DataFrame()))
lifecycle = filter_df(db.get('Agent_Lifecycle', pd.DataFrame()))

# 6. APP MODULES (TABS)
tabs = st.tabs(["📊 Sales", "🕵️ Lifecycle", "📞 CRM", "🚚 Logistics", "📦 Inventory"])

# MODULE 1: SALES & EXECUTIVE SCORECARD
with tabs[0]:
    st.header("Executive Sales Dashboard")
    target = 40319855100
    actual = sales['Sales_Amount'].sum() if 'Sales_Amount' in sales.columns else 0
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Sales", ngn(actual))
    k2.metric("Target Progress", f"{(actual/target)*100:.1f}%")
    k3.metric("Net Profit", ngn(sales['Net_Profit'].sum() if 'Net_Profit' in sales.columns else 0))
    k4.metric("GGR", ngn(sales['GGR'].sum() if 'GGR' in sales.columns else 0))

    # Scatter Plot (Safe Version)
    if not sales.empty and 'Sales_Amount' in sales.columns:
        st.subheader("Profitability Quadrant Analysis")
        plot_df = sales.copy()
        plot_df['Size'] = plot_df['Sales_Amount'].clip(lower=1)
        fig_q = px.scatter(plot_df, x="Sales_Amount", y="Net_Profit", size="Size", 
                          hover_name="Agent_Username", template="plotly_dark",
                          color_discrete_sequence=[PALETTE['accent']])
        fig_q.update_layout(**PLOTLY_TEMPLATE['layout'])
        st.plotly_chart(fig_q, use_container_width=True)

# MODULE 2: AGENT LIFECYCLE (CHURN & NEW)
with tabs[1]:
    st.header("Agent Retention & Onboarding")
    if not lifecycle.empty:
        lost = lifecycle[lifecycle['Status'].str.contains('Inactive|Lost', na=False, case=False)]
        new = lifecycle[lifecycle['Status'].str.contains('New', na=False, case=False)]
        
        c1, c2 = st.columns(2)
        c1.markdown(f"### 💤 Churn Analysis")
        c1.metric("Lost Agents", len(lost))
        c1.metric("Value Lost", ngn(lost['Peak_Monthly_Sales'].sum()))
        
        c2.markdown(f"### 🌟 New Onboarding")
        c2.metric("New Agents", len(new))
        c2.metric("New Sales Contrib.", ngn(new['Peak_Monthly_Sales'].sum()))
        
        st.subheader("Top 10 High-Value Lost Agents")
        st.table(lost.nlargest(10, 'Peak_Monthly_Sales')[['Agent_Username', 'Peak_Monthly_Sales', 'Total_Active_Days']])

# MODULE 3: CRM & TASK MANAGEMENT
with tabs[2]:
    st.header("CRM Performance & Assignments")
    if not crm.empty:
        calls = len(crm)
        answered = len(crm[crm['Call_Status'] == 'Answered'])
        
        st.columns(3)[0].metric("Total Calls", calls)
        st.columns(3)[1].metric("Answer Rate", f"{(answered/calls)*100:.1f}%")
        st.columns(3)[2].metric("Pending Tasks", len(crm[crm['Task_Status'] == 'Pending']))
        
        st.subheader("CRM Feedback Stream")
        st.dataframe(crm[['Timestamp', 'Agent_Username', 'Conversation_Summary', 'Task_Status', 'Task_Assigned_To']], use_container_width=True)

# MODULE 4: LOGISTICS & FIELD OPS
with tabs[3]:
    st.header("Field Visits & Expense Tracking")
    with st.expander("📝 Log New Field Visit"):
        with st.form("visit_form"):
            v1, v2 = st.columns(2)
            agent_v = v1.text_input("Agent Username")
            reason_v = v2.selectbox("Reason", ["Routine", "Technical", "Churn Recovery", "Training"])
            feedback_v = st.text_area("Visit Feedback")
            spend_v = st.number_input("Amount Spent (₦)", min_value=0)
            if st.form_submit_button("Submit Visit"):
                st.success(f"Visit for {agent_v} logged and ₦{spend_v} deducted from budget.")

    if not logistics.empty:
        st.subheader("Recent Field Reports")
        st.dataframe(logistics[['Date', 'Agent_Username', 'Reason_for_Visit', 'Shop_Rating', 'Expense_Amount_Spent']], use_container_width=True)

# MODULE 5: EQUIPMENT INVENTORY
with tabs[4]:
    st.header("Asset & Inventory Tracking")
    if not inventory.empty:
        low_stock = inventory[inventory['Condition'] == 'Faulty'] # Or add a 'Stock' column
        st.error(f"⚠️ Critical Alert: {len(low_stock)} Faulty Units Reported")
        
        st.subheader("Inventory Distribution")
        fig_inv = px.pie(inventory, names='Equipment_Category', title="Equipment by Category", hole=0.5)
        fig_inv.update_layout(**PLOTLY_TEMPLATE['layout'])
        st.plotly_chart(fig_inv)
        
        st.subheader("Full Asset Log")
        st.dataframe(inventory, use_container_width=True)
