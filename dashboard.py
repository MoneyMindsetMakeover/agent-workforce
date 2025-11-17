import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import requests

# ----------------------------------------------------
# STREAMLIT CONFIG
# ----------------------------------------------------
st.set_page_config(
    page_title="ApexxAdams Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------
# STYLES
# ----------------------------------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
    }
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .status-active {
        background: #10b981;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 5px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-idle {
        background: #f59e0b;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 5px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-offline {
        background: #6b7280;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 5px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# GOOGLE SHEETS CONNECTION
# ----------------------------------------------------
@st.cache_resource
def connect_to_sheets():
    try:
        credentials_dict = dict(st.secrets["google_credentials"])
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None


# ----------------------------------------------------
# LOAD CORA DATA
# ----------------------------------------------------
@st.cache_data(ttl=300)
def load_cora_data():
    try:
        sheet_id = st.secrets["CORA_SHEET_ID"]
        client = connect_to_sheets()
        if client:
            sheet = client.open_by_key(sheet_id).sheet1
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            df.columns = df.columns.str.lower().str.replace(" ", "_")
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading CORA data: {e}")
        return pd.DataFrame()


# ----------------------------------------------------
# LOAD OPSI DATA
# ----------------------------------------------------
@st.cache_data(ttl=60)
def load_opsi_data():
    try:
        sheet_id = st.secrets["OPSI_SHEET_ID"]
        client = connect_to_sheets()
        if client:
            sheet = client.open_by_key(sheet_id).sheet1
            data = sheet.get_all_records()
            return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading OPSI data: {e}")
        return pd.DataFrame()


# ----------------------------------------------------
# OPSI TASK CREATION VIA N8N
# ----------------------------------------------------
def create_opsi_task(task_data):
    webhook_url = "https://hackett2k.app.n8n.cloud/webhook/opsi-create-task"
    try:
        response = requests.post(webhook_url, json=task_data)
        return response.json()
    except Exception as e:
        st.error(f"Error creating task: {e}")
        return None


# ----------------------------------------------------
# HEADER
# ----------------------------------------------------
st.markdown('<p class="main-header">ApexxAdams Command Center</p>', unsafe_allow_html=True)
st.write("Multi-Agent System Dashboard - CORA | MARK | OPSI")


# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------
st.sidebar.title("Agent Control Panel")
st.sidebar.markdown("---")

st.sidebar.subheader("Agent Status")
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    st.markdown('<span class="status-active">CORA</span>', unsafe_allow_html=True)
with col2:
    st.markdown('<span class="status-idle">MARK</span>', unsafe_allow_html=True)
with col3:
    st.markdown('<span class="status-active">OPSI</span>', unsafe_allow_html=True)

st.sidebar.markdown("---")

selected_agent = st.sidebar.selectbox(
    "Select Agent",
    ["Dashboard Overview", "CORA (Lead Generation)", "MARK (Marketing AI)", "OPSI (Operations)"]
)

st.sidebar.markdown("---")

st.sidebar.subheader("Quick Actions")
if st.sidebar.button("Run CORA Now"):
    st.sidebar.success("CORA workflow triggered!")
if st.sidebar.button("Ask MARK"):
    st.sidebar.info("MARK chat opening...")
if st.sidebar.button("View OPSI Tasks"):
    st.sidebar.info("Loading OPSI tasks...")

# ----------------------------------------------------
# DASHBOARD OVERVIEW
# ----------------------------------------------------
if selected_agent == "Dashboard Overview":

    cora_df = load_cora_data()
    opsi_df = load_opsi_data()

    # Column safety
    status_col = "Status " if "Status " in opsi_df.columns else "Status"
    priority_col = "Priority " if "Priority " in opsi_df.columns else "Priority"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        pending = len(opsi_df[opsi_df[status_col] == "New"]) if not opsi_df.empty else 0
        st.metric("Pending Tasks", pending)

    with col2:
        in_progress = len(opsi_df[opsi_df[status_col] == "In Progress"]) if not opsi_df.empty else 0
        st.metric("In Progress", in_progress)

    with col3:
        high = len(opsi_df[opsi_df[priority_col] == "High"]) if not opsi_df.empty else 0
        st.metric("High Priority", high)

    with col4:
        st.metric("Overall Performance", "68%" if not cora_df.empty else "N/A")

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="agent-card">
            <h3>CORA</h3>
            <p>Community Outreach & Research Assistant</p>
            <p><strong>Status:</strong> <span class="status-active">Active</span></p>
            <p><strong>Leads Generated:</strong> {len(cora_df)}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="agent-card">
            <h3>MARK</h3>
            <p>Marketing & Engagement Bot</p>
            <p><strong>Status:</strong> <span class="status-idle">Idle</span></p>
            <p><strong>Setup:</strong> In Progress</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="agent-card">
            <h3>OPSI</h3>
            <p>Operations & Policy System</p>
            <p><strong>Status:</strong> <span class="status-active">Active</span></p>
            <p><strong>Tasks:</strong> {len(opsi_df)}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("CORA Recent Leads")
        if not cora_df.empty:
            recent = cora_df.tail(5)[["name", "organization", "email"]]
            st.dataframe(recent, use_container_width=True, hide_index=True)
        else:
            st.info("No CORA leads yet.")

    with col2:
        st.subheader("OPSI Upcoming Tasks")
        if not opsi_df.empty:
            display_cols = ["Title", "Deadline Date", priority_col]
            available = [c for c in display_cols if c in opsi_df.columns]
            st.dataframe(opsi_df[available].head(5), use_container_width=True, hide_index=True)
        else:
            st.info("No OPSI tasks yet.")


# ----------------------------------------------------
# CORA PAGE
# ----------------------------------------------------
elif selected_agent == "CORA (Lead Generation)":

    st.header("CORA - Lead Generation Dashboard")
    df = load_cora_data()

    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Leads", len(df))

        with col2:
            today = datetime.now().strftime("%Y-%m-%d")
            today_leads = df[df["timestamp"].str.contains(today, na=False)] if "timestamp" in df.columns else pd.DataFrame()
            st.metric("Today", len(today_leads))

        with col3:
            cities = df["organization"].str.contains("City", case=False, na=False).sum() if "organization" in df.columns else 0
            st.metric("Cities", cities)

        with col4:
            churches = df["organization"].str.contains("Church", case=False, na=False).sum() if "organization" in df.columns else 0
            st.metric("Churches", churches)

        st.markdown("---")

        search = st.text_input("Search leads...")
        filtered = df.copy()

        if search:
            mask = (
                df["name"].str.contains(search, case=False, na=False)
                | df["email"].str.contains(search, case=False, na=False)
                | df["organization"].str.contains(search, case=False, na=False)
            )
            filtered = df[mask]

        st.subheader(f"All Leads ({len(filtered)})")

        view_cols = ["name", "title", "organization", "email", "suggested_action", "timestamp"]
        available = [col for col in view_cols if col in filtered.columns]

        st.dataframe(filtered[available], use_container_width=True, hide_index=True)

        st.download_button(
            "Export CSV",
            filtered.to_csv(index=False),
            f"cora_leads_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )

    else:
        st.info("No CORA data available.")


# ----------------------------------------------------
# MARK PAGE
# ----------------------------------------------------
elif selected_agent == "MARK (Marketing AI)":

    st.header("MARK - Marketing & Engagement AI")
    st.markdown("""
    ### About MARK
    MARK assists with:
    - Marketing automation
    - SMS/Email campaigns
    - Audience engagement
    - Lead follow-up
    """)

    st.markdown("---")

    st.subheader("Chat with MARK")
    user_input = st.text_input("Ask MARK...")
    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        with st.chat_message("assistant"):
            st.write("I’m MARK. I'm still learning from CORA’s activity.")


# ----------------------------------------------------
# OPSI PAGE
# ----------------------------------------------------
elif selected_agent == "OPSI (Operations)":

    st.header("OPSI - Operations & Policy System")

    opsi_df = load_opsi_data()

    # Safe column handling
    status_col = "Status " if "Status " in opsi_df.columns else "Status"
    priority_col = "Priority " if "Priority " in opsi_df.columns else "Priority"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        pending = len(opsi_df[opsi_df[status_col] == "New"]) if not opsi_df.empty else 0
        st.metric("Pending", pending)

    with col2:
        in_progress = len(opsi_df[opsi_df[status_col] == "In Progress"]) if not opsi_df.empty else 0
        st.metric("In Progress", in_progress)

    with col3:
        high = len(opsi_df[opsi_df[priority_col] == "High"]) if not opsi_df.empty else 0
        st.metric("High Priority", high)

    with col4:
        st.metric("Total Tasks", len(opsi_df))

    st.markdown("---")


    # ----------------------------------------------------
    # CREATE TASK PANEL
    # ----------------------------------------------------
    with st.expander("➕ Create New Task"):
        with st.form("new_task_form"):

            title = st.text_input("Task Title*")

            task_type = st.selectbox(
                "Task Type*",
                ["Select option", "RFP Submission", "Contract Renewal", "Audit", "Compliance Report"]
            )

            assigned_to = st.text_input("Assigned To*", placeholder="Enter name")

            deadline = st.date_input("Deadline Date*")

            priority = st.selectbox(
                "Priority*",
                ["Select option", "High", "Medium", "Low"]
            )

            notes = st.text_area("Notes")

            submitted = st.form_submit_button("Create Task")

            if submitted:
                errors = []

                if not title.strip():
                    errors.append("Task Title is required.")
                if task_type == "Select option":
                    errors.append("Task Type is required.")
                if priority == "Select option":
                    errors.append("Priority is required.")
                if not assigned_to.strip():
                    errors.append("Assigned To is required.")

                if errors:
                    for e in errors:
                        st.error(e)

                else:
                    task_data = {
                        "title": title,
                        "taskType": task_type,
                        "assignedTo": assigned_to,
                        "deadline": str(deadline),
                        "priority": priority,
                        "notes": notes
                    }
                    result = create_opsi_task(task_data)

                    if result:
                        st.success("✅ Task created successfully.")
                        st.cache_data.clear()
                        st.rerun()


    # ----------------------------------------------------
    # ACTIVE TASKS TABLE
    # ----------------------------------------------------
    st.markdown("---")
    st.subheader("Active Tasks")

    if not opsi_df.empty:
        st.dataframe(opsi_df, use_container_width=True, hide_index=True)
    else:
        st.info("No tasks found.")


# ----------------------------------------------------
# FOOTER
# ----------------------------------------------------
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align:center; color:#666; padding:1rem;'>
        <strong>ApexxAdams Multi-Agent Command Center</strong><br>
        Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
    """,
    unsafe_allow_html=True
)
