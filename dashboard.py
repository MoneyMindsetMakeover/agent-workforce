import streamlit as st
from datetime import datetime
from cora import get_cora_status, get_cora_leads
from mark import get_mark_status
from opsi import get_opsi_status, load_opsi_tasks
from utils import load_cora_data, send_approved_leads_to_mark, load_opsi_data, send_opsi_task

# ========================================
# PAGE CONFIGURATION
# ========================================
st.set_page_config(
    page_title="ApexxAdams Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# CUSTOM STYLING
# ========================================
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
    .metric-card {
        background: #f9fafb;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# SIDEBAR NAVIGATION
# ========================================
with st.sidebar:
    st.markdown("### ⚡ ApexxAdams")
    st.markdown("**Multi-Agent Command Center**")
    st.markdown("---")
    
    st.markdown("### 🧭 Navigation")
    selected_page = st.radio(
        "Select View:",
        ["Dashboard Overview", "Approve Leads", "Manage Tasks"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("### 📊 System Status")
    
    # Get agent statuses dynamically
    cora_status = get_cora_status()
    mark_status = get_mark_status()
    opsi_status = get_opsi_status()
    
    # Map status to CSS class
    status_class_map = {
        "Active": "status-active",
        "Idle": "status-idle",
        "Offline": "status-offline"
    }
    
    st.markdown(f'<span class="{status_class_map.get(cora_status, "status-offline")}">● CORA: {cora_status}</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="{status_class_map.get(mark_status, "status-offline")}">● MARK: {mark_status}</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="{status_class_map.get(opsi_status, "status-offline")}">● OPSI: {opsi_status}</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption(f"v2.0 • Last updated: {datetime.now().strftime('%H:%M:%S')}")

# ========================================
# MAIN CONTENT AREA
# ========================================

# Header
st.markdown('<p class="main-header">⚡ ApexxAdams Multi-Agent Command Center</p>', unsafe_allow_html=True)
st.markdown("**Your AI-Powered Business Operations Platform**")
st.markdown("---")

# ========================================
# PAGE ROUTING
# ========================================

if selected_page == "Dashboard Overview":
    # ========================================
    # DASHBOARD OVERVIEW PAGE
    # ========================================
    
    # Agent Status Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_badge = f'<span class="{status_class_map.get(cora_status, "status-offline")}">{cora_status.upper()}</span>'
        st.markdown(f"""
        <div class="agent-card">
            <h3>🎯 CORA</h3>
            <p>Community Outreach & Research Assistant</p>
            <div style="margin-top: 1rem;">
                {status_badge}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status_badge = f'<span class="{status_class_map.get(mark_status, "status-offline")}">{mark_status.upper()}</span>'
        st.markdown(f"""
        <div class="agent-card">
            <h3>📧 MARK</h3>
            <p>Marketing & Research Knowledge</p>
            <div style="margin-top: 1rem;">
                {status_badge}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        status_badge = f'<span class="{status_class_map.get(opsi_status, "status-offline")}">{opsi_status.upper()}</span>'
        st.markdown(f"""
        <div class="agent-card">
            <h3>📋 OPSI</h3>
            <p>Operations & Policy System</p>
            <div style="margin-top: 1rem;">
                {status_badge}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Get data from agents
    cora_leads = get_cora_leads()
    opsi_tasks = load_opsi_tasks()
    
    with col1:
        st.metric("Total Leads", len(cora_leads))
    
    with col2:
        qualified = sum(1 for lead in cora_leads if lead.get('Status') == 'Qualified')
        st.metric("Qualified Leads", qualified)
    
    with col3:
        contacted = sum(1 for lead in cora_leads if lead.get('Status') == 'Contacted')
        st.metric("Contacted", contacted)
    
    with col4:
        pending_tasks = len([t for t in opsi_tasks.to_dict('records') if t.get('Status') == 'New' or t.get('Status ') == 'New']) if not opsi_tasks.empty else 0
        st.metric("Pending Tasks", pending_tasks)
    
    st.markdown("---")
    
    # Recent Activity
    st.subheader("📊 Recent Activity")
    
    if cora_leads:
        import pandas as pd
        recent_df = pd.DataFrame(cora_leads).head(5)
        st.dataframe(recent_df, use_container_width=True, hide_index=True)
    else:
        st.info("No recent activity. Run CORA to generate leads.")

elif selected_page == "Approve Leads":
    # ========================================
    # APPROVE LEADS PAGE
    # ========================================
    
    st.header("📧 Approve Leads for Outreach")
    st.write("Review and approve leads for MARK to send outreach emails")
    
    df = load_cora_data()
    
    if df.empty:
        st.info("No leads available. Run CORA to generate leads.")
    else:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Leads", len(df))
        
        with col2:
            today = datetime.now().strftime("%Y-%m-%d")
            today_count = df["timestamp"].str.contains(today, na=False).sum() if "timestamp" in df.columns else 0
            st.metric("Today", today_count)
        
        with col3:
            cities = df["organization"].str.contains("City", case=False, na=False).sum() if "organization" in df.columns else 0
            st.metric("Cities", cities)
        
        with col4:
            churches = df["organization"].str.contains("Church", case=False, na=False).sum() if "organization" in df.columns else 0
            st.metric("Churches", churches)
        
        st.markdown("---")
        
        # ========================================
        # APPROVE LEADS SECTION
        # ========================================
        if 'Lead ID' in df.columns:
            st.markdown("### Select Leads to Approve")
            
            # Select All checkbox
            col1, col2 = st.columns([1, 5])
            with col1:
                select_all = st.checkbox("Select All", key="select_all_cora")
            with col2:
                st.markdown("*Check the box to select all leads at once*")
            
            st.markdown("---")
            
            # Display leads with checkboxes
            selected_lead_ids = []
            
            # Create a container for better spacing
            for idx, row in df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([0.5, 2, 2.5, 2, 1.5])
                
                with col1:
                    is_selected = st.checkbox(
                        "✓",
                        value=select_all,
                        key=f"lead_check_{row.get('Lead ID', idx)}",
                        label_visibility="collapsed"
                    )
                    if is_selected:
                        selected_lead_ids.append(row.get('Lead ID', ''))
                
                with col2:
                    st.write(f"**{row.get('Name', 'N/A')}**")
                
                with col3:
                    st.write(row.get('Organization', 'N/A'))
                
                with col4:
                    email = row.get('Email', 'N/A')
                    st.write(email[:25] + '...' if len(str(email)) > 25 else email)
                
                with col5:
                    st.code(row.get('Lead ID', 'N/A'), language=None)
            
            st.markdown("---")
            
            # Approval controls
            col1, col2, col3 = st.columns([2, 2, 2])
            
            with col1:
                st.metric("Selected", len(selected_lead_ids))
            
            with col2:
                approve_btn = st.button(
                    "✅ Approve Selected Leads",
                    type="primary",
                    use_container_width=True,
                    disabled=len(selected_lead_ids) == 0
                )
            
            with col3:
                if st.button("🔄 Refresh Data", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()
            
            # Handle approval
            if approve_btn:
                if selected_lead_ids:
                    with st.spinner("Sending to MARK..."):
                        success, response = send_approved_leads_to_mark(selected_lead_ids)
                        
                        if success:
                            st.success(f"✅ Successfully approved {len(selected_lead_ids)} lead(s)!")
                            st.info("🤖 MARK will send outreach emails shortly.")
                            
                            # Show approved leads
                            with st.expander("View Approved Leads"):
                                for lead_id in selected_lead_ids:
                                    st.write(f"• {lead_id}")
                        else:
                            st.error(f"❌ Failed to send to MARK: {response}")
                            st.info("💡 Check that the MARK webhook is running in n8n")
                else:
                    st.warning("⚠️ Please select at least one lead to approve")
        
        st.markdown("---")
        
        # ========================================
        # SEARCH AND FILTER
        # ========================================
        search = st.text_input("🔍 Search leads by name, email, or organization...")
        filtered = df.copy()
        
        if search:
            mask = (
                df["name"].str.contains(search, case=False, na=False) |
                df["email"].str.contains(search, case=False, na=False) |
                df["organization"].str.contains(search, case=False, na=False)
            )
            filtered = df[mask]
        
        # ========================================
        # LEADS TABLE
        # ========================================
        st.subheader(f"All Leads ({len(filtered)})")
        
        if not filtered.empty:
            st.dataframe(filtered, use_container_width=True, hide_index=True)
            
            # Export button
            csv = filtered.to_csv(index=False)
            st.download_button(
                "📥 Export to CSV",
                csv,
                f"cora_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv",
                use_container_width=False
            )
        else:
            st.info("No leads match your search criteria.")

elif selected_page == "Manage Tasks":
    # ========================================
    # MANAGE TASKS PAGE (OPSI)
    # ========================================
    
    st.header("📋 Manage Tasks")
    st.write("Create and track compliance tasks, deadlines, and operations")
    
    opsi_df = load_opsi_data()
    
    # Determine column names (handle trailing spaces)
    status_col = "Status " if "Status " in opsi_df.columns else "Status"
    priority_col = "Priority " if "Priority " in opsi_df.columns else "Priority"
    
    # Metrics
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
    
    # ========================================
    # CREATE TASK
    # ========================================
    with st.expander("➕ Create New Task", expanded=False):
        with st.form("task_form"):
            
            title = st.text_input("Task Title*")
            
            task_type = st.selectbox(
                "Task Type*",
                ["Select option", "RFP Submission", "Contract Renewal", "Audit", "Compliance Report", "Other"]
            )
            
            assigned_to = st.text_input("Assigned To*", placeholder="Enter person name")
            
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
                    errors.append("Task title is required.")
                if task_type == "Select option":
                    errors.append("Task type is required.")
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
                        "notes": notes,
                    }
                    result = send_opsi_task(task_data)
                    
                    if result:
                        st.success("✅ Task created successfully!")
                        st.cache_data.clear()
                        st.rerun()
    
    st.markdown("---")
    
    # ========================================
    # ACTIVE TASKS
    # ========================================
    st.subheader("Active Tasks")
    
    if not opsi_df.empty:
        st.dataframe(opsi_df, hide_index=True, use_container_width=True)
    else:
        st.info("No tasks found. Create your first task above.")

# ========================================
# FOOTER
# ========================================
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p><strong>ApexxAdams Multi-Agent Command Center</strong></p>
        <p>CORA | MARK | OPSI | Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    """,
    unsafe_allow_html=True
)
