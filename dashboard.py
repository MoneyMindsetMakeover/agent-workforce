import streamlit as st
import pandas as pd
import requests

# Local Modules
from cora import get_cora_status, get_cora_leads
from mark import get_mark_status
from opsi import (
    get_opsi_status,
    load_opsi_tasks,
    create_opsi_task
)

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="ApexxAdams Command Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.title("Agent Control Panel")

# ---- Agent Status ----
st.sidebar.subheader("Agent Status")

cora_status = get_cora_status()
mark_status = get_mark_status()
opsi_status = get_opsi_status()

st.sidebar.markdown(
    f"""
    <div style="margin-bottom:10px;">
        <span style="background:{'#2ecc71' if cora_status=='Active' else '#e74c3c'};padding:4px 8px;border-radius:4px;color:white;">CORA</span>
        <span style="background:{'#2ecc71' if mark_status=='Active' else '#e74c3c'};padding:4px 8px;border-radius:4px;color:white;">MARK</span>
        <span style="background:{'#2ecc71' if opsi_status=='Active' else '#e74c3c'};padding:4px 8px;border-radius:4px;color:white;">OPSI</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ---- Select Agent (Navigation) ----
st.sidebar.subheader("Select Agent")

agent_page = st.sidebar.selectbox(
    "Dashboard Overview",
    ["Dashboard Overview", "CORA (Outreach)", "MARK (Marketing)", "OPSI (Operations)"]
)

# ---- Quick Actions ----
st.sidebar.subheader("Quick Actions")

# -------------------------
# CORA Manual Trigger Function
# -------------------------
def trigger_cora():
    try:
        url = st.secrets["CORA_WEBHOOK_URL"]
        
        with st.spinner("Running CORA..."):
            response = requests.post(url, timeout=30)
        
        if response.status_code == 200:
            try:
                leads = response.json()
                st.success(f"✅ CORA generated new leads!")
            except:
                st.success("✅ CORA workflow started successfully!")
        else:
            st.error(f"Failed → {response.status_code}")
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ---- RUN CORA ----
if st.sidebar.button("Run CORA Now"):
    trigger_cora()

# ---- ASK MARK (Webhook Placeholder) ----
def trigger_mark():
    try:
        url = st.secrets["MARK_WEBHOOK_URL"]
        res = requests.post(url, timeout=30)

        if res.status_code == 200:
            st.success("MARK has started running.")
        else:
            st.error(f"Failed to trigger MARK → {res.status_code}: {res.text}")

    except Exception as e:
        st.error(f"Error triggering MARK: {e}")

if st.sidebar.button("Ask MARK"):
    trigger_mark()

# ---- OPSI Tasks ----
if st.sidebar.button("View OPSI Tasks"):
    agent_page = "OPSI (Operations)"

# -------------------------
# MAIN DASHBOARD LOGIC
# -------------------------
st.title("ApexxAdams Command Center")
st.write("Multi-Agent System Dashboard — CORA | MARK | OPSI")
st.markdown("---")

# ----------------------------------------------------------------
#                     DASHBOARD OVERVIEW PAGE
# ----------------------------------------------------------------
if agent_page == "Dashboard Overview":

    col1, col2, col3, col4 = st.columns(4)

    # CORA Leads
    cora_leads = get_cora_leads()

    with col1:
        st.metric("Pending Tasks", len(load_opsi_tasks()))
    with col2:
        st.metric("CORA Leads", len(cora_leads))
    with col3:
        st.metric("AGENTS ACTIVE", sum([cora_status=="Active", mark_status=="Active", opsi_status=="Active"]))
    with col4:
        st.metric("Overall Performance", "N/A")

    st.markdown("---")

    # ---- Agent Cards ----
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### CORA")
        st.markdown("Community Outreach & Research Assistant")
        st.write(f"**Status:** {cora_status}")
        st.write(f"**Leads Generated:** {len(cora_leads)}")

    with c2:
        st.markdown("### MARK")
        st.markdown("Marketing & Engagement Bot")
        st.write(f"**Status:** {mark_status}")
        st.write("**Setup:** In Progress")

    with c3:
        st.markdown("### OPSI")
        st.markdown("Operations & Policy System")
        st.write(f"**Status:** {opsi_status}")
        st.write(f"**Tasks:** {len(load_opsi_tasks())}")

    st.markdown("---")

    # CORA Leads Preview
st.subheader("CORA Recent Leads")
if len(cora_leads) == 0:
    st.info("No leads yet. Run CORA to generate leads.")
else:
    cora_df_display = pd.DataFrame(cora_leads)
    st.dataframe(cora_df_display)
    
    st.download_button(
        "Export CSV",
        cora_df_display.to_csv(index=False),
        f"cora_leads_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv"
    )

# ----------------------------------------------------------------
#                        CORA PAGE
# ----------------------------------------------------------------
elif agent_page == "CORA (Outreach)":
    st.header("CORA — Community Outreach & Research Assistant")

    leads = get_cora_leads()
    if len(leads) == 0:
        st.info("No leads have been generated yet.")
    else:
        st.dataframe(pd.DataFrame(leads))

# ----------------------------------------------------------------
#                        MARK PAGE
# ----------------------------------------------------------------
elif agent_page == "MARK (Marketing)":
    st.header("MARK — Marketing & Engagement Bot")
    st.write("MARK is configured to handle email interactions, replies, and follow-ups.")

    st.write(f"**Status:** {mark_status}")

# ----------------------------------------------------------------
#                        OPSI PAGE
# ----------------------------------------------------------------
elif agent_page == "OPSI (Operations)":

    st.header("OPSI — Operations & Policy System")

    opsi_df = load_opsi_tasks()

    # Metrics
    colA, colB, colC = st.columns(3)

    with colA:
        pending = len(opsi_df[opsi_df["Status"] == "New"]) if not opsi_df.empty else 0
        st.metric("Pending", pending)

    with colB:
        in_progress = len(opsi_df[opsi_df["Status"] == "In Progress"]) if not opsi_df.empty else 0
        st.metric("In Progress", in_progress)

    with colC:
        high_priority = len(opsi_df[opsi_df["Priority"] == "High"]) if not opsi_df.empty else 0
        st.metric("High Priority", high_priority)

    st.markdown("---")

    # TASK LIST
    st.subheader("OPSI Tasks")
    if opsi_df.empty:
        st.info("No OPSI tasks found.")
    else:
        st.dataframe(opsi_df)

    st.markdown("---")

    # CREATE NEW TASK
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
                        st.success("Task created successfully.")
                        st.cache_data.clear()
                        st.rerun()








