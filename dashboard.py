import streamlit as st
from datetime import datetime
import pandas as pd
from daphne import get_daphne_status, get_daphne_leads
from diana import get_diana_status
from opsi import get_opsi_status, load_opsi_tasks
from utils import load_daphne_data, send_approved_leads_to_diana, load_opsi_data, send_opsi_task, update_opsi_task

# ========================================
# PAGE CONFIGURATION
# ========================================
st.set_page_config(
    page_title="Money Mindset Makeover Command Center",
    page_icon="💰",
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
        background: linear-gradient(135deg, #2E7D32 0%, #1B5E20 100%);
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
        border-left: 4px solid #2E7D32;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# SIDEBAR NAVIGATION
# ========================================
with st.sidebar:
    st.markdown("### 💰 Money Mindset Makeover")
    st.markdown("**Multi-Agent Command Center**")
    st.markdown("---")
    
    st.markdown("### 🧭 Navigation")
    
    # Initialize session state for page selection
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "Dashboard Overview"
    
    selected_page = st.radio(
        "Select View:",
        ["Dashboard Overview", "Approve Leads", "Manage Tasks"],
        index=["Dashboard Overview", "Approve Leads", "Manage Tasks"].index(st.session_state.selected_page),
        label_visibility="collapsed"
    )
    
    # Update session state when radio changes
    if selected_page != st.session_state.selected_page:
        st.session_state.selected_page = selected_page
    
    st.markdown("---")
    st.markdown("### 📊 System Status")
    
    # Get agent statuses dynamically
    daphne_status = get_daphne_status()
    diana_status = get_diana_status()
    opsi_status = get_opsi_status()
    
    # Map status to CSS class
    status_class_map = {
        "Active": "status-active",
        "Idle": "status-idle",
        "Offline": "status-offline"
    }
    
    st.markdown(f'<span class="{status_class_map.get(daphne_status, "status-offline")}">● DAPHNE: {daphne_status}</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="{status_class_map.get(diana_status, "status-offline")}">● DIANA: {diana_status}</span>', unsafe_allow_html=True)
    st.markdown(f'<span class="{status_class_map.get(opsi_status, "status-offline")}">● OPSI: {opsi_status}</span>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption(f"v3.0 • Last updated: {datetime.now().strftime('%H:%M:%S')}")

# ========================================
# MAIN CONTENT AREA
# ========================================

# Header
st.markdown('<p class="main-header" style="color: #2E7D32;">💰 Money Mindset Makeover</p>', unsafe_allow_html=True)
st.markdown("**Multi-Agent Command Center**")
st.markdown("---")

# ========================================
# PAGE ROUTING
# ========================================

if st.session_state.selected_page == "Dashboard Overview":
    # ========================================
    # DASHBOARD OVERVIEW PAGE
    # ========================================
    
    # Agent Status Cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_badge = f'<span class="{status_class_map.get(daphne_status, "status-offline")}">{daphne_status.upper()}</span>'
        st.markdown(f"""
        <div class="agent-card">
            <h3>🎯 DAPHNE</h3>
            <p>Donor & Partner Prospecting Engine</p>
            <div style="margin-top: 1rem;">
                {status_badge}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status_badge = f'<span class="{status_class_map.get(diana_status, "status-offline")}">{diana_status.upper()}</span>'
        st.markdown(f"""
        <div class="agent-card">
            <h3>💬 DIANA</h3>
            <p>Donor Intelligence & Nurture Agent</p>
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
    daphne_leads = get_daphne_leads()
    opsi_tasks_df = load_opsi_tasks()
    
    with col1:
        st.metric("Total Donor Prospects", len(daphne_leads))
    
    with col2:
        approved = sum(1 for lead in daphne_leads if lead.get('Status') == 'approved')
        st.metric("Approved Prospects", approved)
    
    with col3:
        # FIX: Check if DataFrame and handle properly
        if not opsi_tasks_df.empty and 'Status' in opsi_tasks_df.columns:
            pending = len(opsi_tasks_df[opsi_tasks_df['Status'] == 'New'])
        else:
            pending = 0
        st.metric("Pending Tasks", pending)
    
    with col4:
        st.metric("Active Tasks", len(opsi_tasks_df) if not opsi_tasks_df.empty else 0)
    
    st.markdown("---")
    
    # Recent Activity
    st.subheader("📊 Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Recent Donor Prospects (DAPHNE)**")
        if daphne_leads:
            recent_df = pd.DataFrame(daphne_leads).head(5)
            display_cols = ['Donor ID', 'Name', 'Organization', 'Status']
            available_cols = [col for col in display_cols if col in recent_df.columns]
            st.dataframe(recent_df[available_cols] if available_cols else recent_df, hide_index=True, use_container_width=True)
        else:
            st.info("No donor prospects yet.")
    
    with col2:
        st.markdown("**Recent Tasks (OPSI)**")
        if not opsi_tasks_df.empty:
            recent_tasks = opsi_tasks_df.head(5)
            task_cols = ['Task ID', 'Task Title', 'Status', 'Priority']
            available_cols = [col for col in task_cols if col in recent_tasks.columns]
            st.dataframe(recent_tasks[available_cols] if available_cols else recent_tasks, hide_index=True, use_container_width=True)
        else:
            st.info("No tasks yet.")

elif st.session_state.selected_page == "Approve Leads":
    # ========================================
    # APPROVE LEADS PAGE
    # ========================================
    
    st.subheader("🎯 Review & Approve DAPHNE Prospects")
    st.markdown("Review donor prospects researched by DAPHNE and approve them for DIANA outreach.")
    st.markdown("---")
    
    # Load DAPHNE data
    daphne_df = load_daphne_data()
    
    if not daphne_df.empty:
        # Filter for pending leads
        status_col = "Status" if "Status" in daphne_df.columns else "status"
        
        if status_col in daphne_df.columns:
            # Accept "pending review" status from n8n workflow
pending_df = daphne_df[daphne_df[status_col].str.lower().str.strip() == 'pending review']
            
            if not pending_df.empty:
                st.markdown(f"**{len(pending_df)} prospects awaiting review**")
                
                # Display pending leads
                display_cols = ['Donor ID', 'Name', 'Organization', 'Email', 'Support Type', 'Reason']
                available_cols = [col for col in display_cols if col in pending_df.columns]
                
                st.dataframe(
                    pending_df[available_cols],
                    hide_index=True,
                    use_container_width=True
                )
                
                st.markdown("---")
                
                # Approval section
                st.subheader("✅ Approve Prospects")
                
                # Get Donor ID column (handle variations)
                donor_id_col = "Donor ID" if "Donor ID" in pending_df.columns else "DonorID"
                
                if donor_id_col in pending_df.columns:
                    # Multi-select for leads
                    donor_options = {
                        f"{row[donor_id_col]} - {row.get('Name', 'N/A')} ({row.get('Organization', 'N/A')})": row[donor_id_col]
                        for _, row in pending_df.iterrows()
                    }
                    
                    selected_leads = st.multiselect(
                        "Select prospects to approve for DIANA outreach:",
                        options=list(donor_options.keys()),
                        key="lead_approval_multiselect"
                    )
                    
                    if selected_leads:
                        st.markdown(f"**{len(selected_leads)} prospect(s) selected**")
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col2:
                            if st.button("✅ Approve Selected", type="primary", use_container_width=True):
                                # Get the actual Donor IDs
                                approved_ids = [donor_options[lead] for lead in selected_leads]
                                
                                # Send to DIANA
                                success, response = send_approved_leads_to_diana(approved_ids)
                                
                                if success:
                                    st.success(f"✅ {len(approved_ids)} prospects approved and sent to DIANA!")
                                    st.cache_data.clear()
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed to approve prospects: {response}")
                else:
                    st.warning("⚠️ Donor ID column not found in data")
            else:
                st.info("✨ All prospects have been reviewed! No pending approvals.")
        else:
            st.warning("⚠️ Status column not found in data")
    else:
        st.info("No DAPHNE data available. Check Google Sheets connection.")

elif st.session_state.selected_page == "Manage Tasks":
    # ========================================
    # MANAGE TASKS PAGE (OPSI)
    # ========================================
    
    st.subheader("📋 OPSI Task Management")
    st.markdown("Manage tasks, RFPs, and operational workflows.")
    st.markdown("---")
    
    # Success message from previous update
    if 'update_success_msg' in st.session_state:
        st.success(st.session_state.update_success_msg)
        del st.session_state.update_success_msg
    
    # ========================================
    # CREATE NEW TASK
    # ========================================
    st.subheader("📝 Create New Task")
    
    with st.form("new_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            task_title = st.text_input("Task Title *")
            task_type = st.selectbox(
                "Task Type *",
                ["RFP Submission", "Grant Application", "Partnership Outreach", "Program Development", "Other"]
            )
            assigned_to = st.text_input("Assigned To")
        
        with col2:
            deadline = st.date_input("Deadline")
            status = st.selectbox(
                "Status *",
                ["New", "In Progress", "Completed", "On Hold", "Cancelled"]
            )
            priority = st.selectbox(
                "Priority *",
                ["High", "Medium", "Low"]
            )
        
        notes = st.text_area("Notes")
        
        submitted = st.form_submit_button("📋 Create Task", use_container_width=True, type="primary")
        
        if submitted:
            if task_title and task_type:
                # Generate Task ID
                task_id = f"TASK-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                
                task_data = {
                    "taskId": task_id,
                    "taskType": task_type,
                    "title": task_title,
                    "assignedTo": assigned_to,
                    "deadline": str(deadline),
                    "status": status,
                    "priority": priority,
                    "notes": notes,
                    "timestamp": datetime.now().isoformat()
                }
                
                result = send_opsi_task(task_data)
                
                if result:
                    st.success(f"✅ Task {task_id} created successfully!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Failed to create task")
            else:
                st.error("❌ Please fill in all required fields (*)")
    
    st.markdown("---")
    
    # ========================================
    # UPDATE EXISTING TASK
    # ========================================
    st.subheader("✏️ Update Task")
    
    opsi_df = load_opsi_data()
    
    if not opsi_df.empty:
        # Initialize search state
        if 'task_id_search' not in st.session_state:
            st.session_state.task_id_search = ""
        
        # Get column names (handle variations)
        task_id_col = "Task ID" if "Task ID" in opsi_df.columns else "TaskID"
        task_title_col = "Task Title" if "Task Title" in opsi_df.columns else "Title"
        status_col = "Status" if "Status" in opsi_df.columns else "status"
        priority_col = "Priority" if "Priority" in opsi_df.columns else "priority"
        
        # Search box
        task_id_search = st.text_input(
            "🔍 Search by Task ID:",
            value=st.session_state.task_id_search,
            key="task_search_input"
        )
        
        # Update session state
        st.session_state.task_id_search = task_id_search
        
        # Filter tasks based on search
        if not opsi_df.empty and task_id_col in opsi_df.columns and task_title_col in opsi_df.columns:
            filtered_opsi_df = opsi_df.copy()
            
            if task_id_search.strip():
                filtered_opsi_df = opsi_df[
                    opsi_df[task_id_col].str.contains(task_id_search, case=False, na=False)
                ]
            
            if not filtered_opsi_df.empty:
                task_options = {
                    f"{row[task_id_col]} - {row[task_title_col]}": row[task_id_col] 
                    for _, row in filtered_opsi_df.iterrows()
                }
                
                selected_task_label = st.selectbox(
                    "Select Task:",
                    options=list(task_options.keys()),
                    key=f"task_selector_{len(task_options)}"
                )
                
                if selected_task_label:
                    selected_task_id = task_options[selected_task_label]
                    
                    # Get current task details
                    task_row = opsi_df[opsi_df[task_id_col] == selected_task_id].iloc[0]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Current Details:**")
                        st.write(f"**Task Type:** {task_row.get('Task Type', 'N/A')}")
                        st.write(f"**Title:** {task_row[task_title_col]}")
                        st.write(f"**Status:** {task_row[status_col]}")
                        st.write(f"**Priority:** {task_row[priority_col]}")
                        st.write(f"**Assigned To:** {task_row.get('Assigned To', 'N/A')}")
                        st.write(f"**Deadline:** {task_row.get('Deadline Date', 'N/A')}")
                    
                    with col2:
                        st.markdown("**Update:**")
                        
                        # Initialize session state for form fields
                        if f'form_title_{selected_task_id}' not in st.session_state:
                            st.session_state[f'form_title_{selected_task_id}'] = task_row[task_title_col]
                        if f'form_assigned_{selected_task_id}' not in st.session_state:
                            st.session_state[f'form_assigned_{selected_task_id}'] = task_row.get('Assigned To', '')
                        if f'form_deadline_{selected_task_id}' not in st.session_state:
                            current_deadline = task_row.get('Deadline Date', '')
                            if current_deadline and current_deadline != 'N/A':
                                try:
                                    import datetime as dt
                                    st.session_state[f'form_deadline_{selected_task_id}'] = dt.datetime.strptime(str(current_deadline), '%Y-%m-%d').date()
                                except:
                                    st.session_state[f'form_deadline_{selected_task_id}'] = dt.date.today()
                            else:
                                import datetime as dt
                                st.session_state[f'form_deadline_{selected_task_id}'] = dt.date.today()
                        
                        # Title input
                        new_title = st.text_input(
                            "Title:",
                            value=st.session_state[f'form_title_{selected_task_id}'],
                            key=f"new_title_{selected_task_id}"
                        )
                        
                        # Assigned To input
                        new_assigned_to = st.text_input(
                            "Assigned To:",
                            value=st.session_state[f'form_assigned_{selected_task_id}'],
                            key=f"new_assigned_to_{selected_task_id}"
                        )
                        
                        # Deadline input
                        new_deadline = st.date_input(
                            "Deadline:",
                            value=st.session_state[f'form_deadline_{selected_task_id}'],
                            key=f"new_deadline_{selected_task_id}"
                        )
                        
                        # Status selection
                        current_status_index = 0
                        status_options = ["New", "In Progress", "Completed", "On Hold", "Cancelled"]
                        if task_row[status_col] in status_options:
                            current_status_index = status_options.index(task_row[status_col])
                        
                        new_status = st.selectbox(
                            "Status:",
                            options=status_options,
                            index=current_status_index,
                            key=f"new_status_select_{selected_task_id}"
                        )
                        
                        # Priority selection
                        current_priority_index = 1
                        priority_options = ["High", "Medium", "Low"]
                        if task_row[priority_col] in priority_options:
                            current_priority_index = priority_options.index(task_row[priority_col])
                        
                        new_priority = st.selectbox(
                            "Priority:",
                            options=priority_options,
                            index=current_priority_index,
                            key=f"new_priority_select_{selected_task_id}"
                        )
                        
                        update_notes = st.text_area(
                            "Notes:", 
                            value=task_row.get('Notes', ''), 
                            key=f"update_notes_{selected_task_id}"
                        )
                        
                        if st.button("💾 Update Task", type="primary", use_container_width=True, key=f"update_btn_{selected_task_id}"):
                            update_data = {
                                "taskId": selected_task_id,
                                "taskType": task_row.get('Task Type', 'RFP Submission'),
                                "title": new_title,
                                "assignedTo": new_assigned_to,
                                "deadline": str(new_deadline),
                                "status": new_status,
                                "priority": new_priority,
                                "notes": update_notes
                            }
                            
                            result = update_opsi_task(update_data)
                            
                            if result:
                                st.session_state.update_success_msg = f"✅ Task {selected_task_id} updated successfully!"
                                st.session_state.task_id_search = ""
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("❌ Failed to update task")
            else:
                st.warning(f"⚠️ No tasks found matching '{task_id_search}'")
        else:
            st.warning("⚠️ Task ID or Title column not found in data")
    
    st.markdown("---")
    
    # ========================================
    # ACTIVE TASKS
    # ========================================
    st.subheader("Active Tasks")
    
    if not opsi_df.empty:
        # Add search/filter
        search_task = st.text_input("🔍 Search tasks by title, assignee, or type...", key="task_search")
        
        filtered_tasks = opsi_df.copy()
        if search_task:
            assigned_col = "Assigned To" if "Assigned To" in opsi_df.columns else "AssignedTo"
            task_type_col = "Task Type" if "Task Type" in opsi_df.columns else "TaskType"
            
            mask = (
                opsi_df[task_title_col].str.contains(search_task, case=False, na=False) |
                opsi_df.get(assigned_col, pd.Series(dtype='object')).str.contains(search_task, case=False, na=False) |
                opsi_df.get(task_type_col, pd.Series(dtype='object')).str.contains(search_task, case=False, na=False)
            )
            filtered_tasks = opsi_df[mask]
        
        st.dataframe(filtered_tasks, hide_index=True, use_container_width=True)
    else:
        st.info("No tasks found. Create your first task above.")

# ========================================
# FOOTER
# ========================================
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p><strong>Money Mindset Makeover - Multi-Agent Command Center</strong></p>
        <p>DAPHNE | DIANA | OPSI | Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    """,
    unsafe_allow_html=True
)

