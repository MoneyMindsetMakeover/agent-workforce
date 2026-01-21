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
    st.caption(f"v2.0 • Last updated: {datetime.now().strftime('%H:%M:%S')}")

# ========================================
# MAIN CONTENT AREA
# ========================================

# Header
st.markdown('<p class="main-header" style="color: #ffffff;">💰 Money Mindset Makeover</p>', unsafe_allow_html=True)
st.markdown("**Your AI-Powered Business Operations Platform**")
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
    opsi_tasks = load_opsi_tasks()
    
    with col1:
        st.metric("Pending Review", len(daphne_leads))
    
    with col2:
        qualified = sum(1 for lead in daphne_leads if lead.get('Status') == 'Qualified')
        st.metric("Qualified Leads", qualified)
    
    with col3:
        contacted = sum(1 for lead in daphne_leads if lead.get('Status') == 'Contacted')
        st.metric("Contacted", contacted)
    
    with col4:
        pending_tasks = len([t for t in opsi_tasks.to_dict('records') if t.get('Status') == 'New' or t.get('Status ') == 'New']) if not opsi_tasks.empty else 0
        st.metric("Pending Tasks", pending_tasks)
    
    st.markdown("---")
    
    # Recent Activity - Two Columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📊 Recent Leads")
        if daphne_leads:
            recent_df = pd.DataFrame(daphne_leads).head(5)
            st.dataframe(recent_df, use_container_width=True, hide_index=True)
            
            # Add Approve Leads button
            if st.button("Approve Leads", use_container_width=True, type="primary"):
                st.session_state.selected_page = "Approve Leads"
                st.rerun()
        else:
            st.info("No recent leads. Run CORA to generate leads.")
    
    with col2:
        st.markdown("### 🔥 High Priority Pending Tasks")
        if not opsi_tasks.empty:
            # Determine column names (handle trailing spaces)
            status_col = "Status " if "Status " in opsi_tasks.columns else "Status"
            priority_col = "Priority " if "Priority " in opsi_tasks.columns else "Priority"
            task_id_col = "Task ID" if "Task ID" in opsi_tasks.columns else "OPSI ID"
            task_title_col = "Task Title" if "Task Title" in opsi_tasks.columns else "Title"
            
            # Filter for High Priority + New/Pending status
            high_priority_pending = opsi_tasks[
                (opsi_tasks[priority_col] == "High") & 
                (opsi_tasks[status_col].isin(["New", "Pending"]))
            ].head(5)
            
            if not high_priority_pending.empty:
                # Display each task with quick update option
                for idx, task in high_priority_pending.iterrows():
                    with st.container():
                        col_a, col_b = st.columns([4, 1])
                        
                        with col_a:
                            task_title = task.get(task_title_col, 'N/A')
                            st.write(f"**{task_title}**")
                            st.caption(f"⏰ Deadline: {task.get('Deadline Date', 'N/A')} | 👤 {task.get('Assigned To', 'N/A')}")
                        
                        with col_b:
                            # Navigate to Manage Tasks button
                            if st.button("Start", key=f"quick_start_{idx}", help="Go to Manage Tasks", use_container_width=True):
                                st.session_state.selected_page = "Manage Tasks"
                                st.rerun()
                        
                        st.divider()
            else:
                st.success("✅ No high priority pending tasks")
        else:
            st.info("No tasks available")

elif st.session_state.selected_page == "Approve Leads":
    # ========================================
    # APPROVE LEADS PAGE
    # ========================================
    
    st.header("📧 Approve Donor Prospects for DIANA Outreach")
    st.write("Review and approve prospects for DIANA to send outreach emails")
    
    df = load_daphne_data()
    
    if df.empty:
        st.info("No donor prospects available. Run DAPHNE to generate leads.")
    else:
        # Filter for "pending review" status
        status_col = "Status" if "Status" in df.columns else "status"
        if status_col in df.columns:
            # Accept "pending review" status from n8n workflow
            df = df[df[status_col].str.lower().str.strip() == 'pending review']
        
        if df.empty:
            st.info("✨ All prospects have been reviewed! No pending approvals.")
        else:
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
        
            with col1:
                st.metric("Pending Review", len(df))
        
            with col2:
                today = datetime.now().strftime("%Y-%m-%d")
                today_count = df["timestamp"].str.contains(today, na=False).sum() if "timestamp" in df.columns else 0
                st.metric("Today", today_count)
        
            with col3:
                foundations = df.get("Donor Type", pd.Series(dtype="str")).str.contains("Foundation", case=False, na=False).sum() if "organization" in df.columns else 0
                st.metric("Foundations", foundations)
        
            with col4:
                corporates = df.get("Donor Type", pd.Series(dtype="str")).str.contains("Corporate", case=False, na=False).sum() if "organization" in df.columns else 0
                st.metric("Corporates", corporates)
        
            st.markdown("---")
        
            # ========================================
            # APPROVE LEADS SECTION
            # ========================================
            if 'Donor ID' in df.columns:
                st.markdown("### Select Prospects to Approve")
            
                # Select All checkbox
                col1, col2 = st.columns([1, 5])
                with col1:
                    select_all = st.checkbox("Select All", key="select_all_daphne")
                with col2:
                    st.markdown("*Check the box to select all prospects at once*")
            
                # TOP APPROVE BUTTON
                col1, col2, col3 = st.columns([2, 2, 2])
                with col1:
                    if st.button("🔄 Refresh Data", use_container_width=True, key="refresh_top"):
                        st.cache_data.clear()
                        st.rerun()
                with col2:
                    approve_btn_top = st.button(
                        "✅ Approve Selected Prospects",
                        type="primary",
                        use_container_width=True,
                        key="approve_top"
                    )
            
                st.markdown("---")
            
                # Display leads with checkboxes in container with fixed height
                selected_donor_ids = []
            
                # Create scrollable container using st.container with height parameter
                leads_container = st.container(height=500)
            
                with leads_container:
                    for idx, row in df.iterrows():
                        col1, col2, col3, col4, col5 = st.columns([0.5, 2, 2.5, 2, 1.5])
                    
                        with col1:
                            is_selected = st.checkbox(
                                "✓",
                                value=select_all,
                                key=f"donor_check_{idx}",
                                label_visibility="collapsed"
                            )
                            if is_selected:
                                donor_id = row.get('Donor ID', '')
                                if donor_id:
                                    selected_donor_ids.append(donor_id)
                    
                        with col2:
                            st.write(f"**{row.get('Name', 'N/A')}**")
                    
                        with col3:
                            st.write(row.get('Organization', 'N/A'))
                    
                        with col4:
                            email = row.get('Email', 'N/A')
                            st.write(email[:25] + '...' if len(str(email)) > 25 else email)
                    
                        with col5:
                            st.code(row.get('Donor ID', 'N/A'), language=None)
            
                st.markdown("---")
            
                # Approval controls
                col1, col2, col3 = st.columns([2, 2, 2])
            
                with col1:
                    st.metric("Selected", len(selected_donor_ids))
            
                with col2:
                    approve_btn_bottom = st.button(
                        "✅ Approve Selected Prospects",
                        type="primary",
                        use_container_width=True,
                        disabled=len(selected_donor_ids) == 0,
                        key="approve_bottom"
                    )
            
                with col3:
                    if st.button("🔄 Refresh Data", use_container_width=True):
                        st.cache_data.clear()
                        st.rerun()
            
                # Handle approval from either button
                if approve_btn_top or approve_btn_bottom:
                    if selected_donor_ids:
                        with st.spinner("Sending to MARK..."):
                            success, response = send_approved_leads_to_diana(selected_donor_ids)
                        
                            if success:
                                st.success(f"✅ Successfully approved {len(selected_donor_ids)} prospect(s)!")
                                st.info("🤖 DIANA will send outreach emails shortly.")
                            
                                # Show approved leads
                                with st.expander("View Approved Prospects"):
                                    for donor_id in selected_donor_ids:
                                        st.write(f"• {donor_id}")
                            else:
                                st.error(f"❌ Failed to send to DIANA: {response}")
                                st.info("💡 Check that the DIANA webhook is running in n8n")
                    else:
                        st.warning("⚠️ Please select at least one prospect to approve")
        
            st.markdown("---")
        
            # ========================================
            # SEARCH AND FILTER
            # ========================================
        search = st.text_input("🔍 Search prospects by name, email, or organization...")
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
            st.info("No prospects match your search criteria.")

elif st.session_state.selected_page == "Manage Tasks":
    # ========================================
    # MANAGE TASKS PAGE (OPSI)
    # ========================================
    
    # Scroll anchor at top
    st.markdown('<div id="manage-tasks-top"></div>', unsafe_allow_html=True)
    
    st.header("📋 Manage Tasks")
    st.write("Create and track compliance tasks, deadlines, and operations")
    
    opsi_df = load_opsi_data()
    
    # Determine column names (handle trailing spaces)
    status_col = "Status " if "Status " in opsi_df.columns else "Status"
    priority_col = "Priority " if "Priority " in opsi_df.columns else "Priority"
    task_id_col = "Task ID" if "Task ID" in opsi_df.columns else "OPSI ID"
    task_title_col = "Task Title" if "Task Title" in opsi_df.columns else "Title"
    
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
    
    # Show success message if it exists in session state
    if 'create_success_msg' in st.session_state:
        st.success(st.session_state.create_success_msg)
        del st.session_state.create_success_msg
    
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
                    
                    # Show processing message
                    with st.spinner("Creating task..."):
                        result = send_opsi_task(task_data)
                    
                    if result:
                        # Store success message in session state before rerun
                        st.session_state.create_success_msg = f"✅ Task '{title}' created successfully!"
                        st.cache_data.clear()
                        st.markdown("""
                        <script>
                            window.parent.document.querySelector('[data-testid="stAppViewContainer"]').scrollTop = 0;
                        </script>
                        """, unsafe_allow_html=True)
                        st.rerun()
                    else:
                        st.error("❌ Failed to create task. Check that the OPSI webhook is running in n8n.")
    
    # ========================================
    # UPDATE TASK SECTION
    # ========================================
    
    # Show success message if it exists in session state
    if 'update_success_msg' in st.session_state:
        st.success(st.session_state.update_success_msg)
        del st.session_state.update_success_msg
    
    # Keep expander open if search is active OR task is selected
    is_expanded = (st.session_state.get('task_id_search', '') != '' or 
                   st.session_state.get('selected_task_id') is not None)
    
    with st.expander("✏️ Update Task", expanded=is_expanded):
        st.markdown("**Select a task to update**")
        
        # Initialize session state for search
        if 'task_id_search' not in st.session_state:
            st.session_state.task_id_search = ""
        
        # Search Task ID field
        task_id_search = st.text_input(
            "🔍 Search Task ID:",
            value=st.session_state.task_id_search,
            placeholder="Enter Task ID to filter...",
            key="task_id_search_input"
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
                
                # Initialize selected task in session state
                if 'selected_task_id' not in st.session_state:
                    st.session_state.selected_task_id = None
                
                # Get the current index for the selectbox
                current_index = 0
                task_ids = list(task_options.values())
                if st.session_state.selected_task_id in task_ids:
                    current_index = task_ids.index(st.session_state.selected_task_id)
                
                selected_task_label = st.selectbox(
                    "Select Task:",
                    options=list(task_options.keys()),
                    index=current_index,
                    key="task_selector_fixed"
                )
                
                if selected_task_label:
                    selected_task_id = task_options[selected_task_label]
                    st.session_state.selected_task_id = selected_task_id
                    
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
                                # Store success message in session state before rerun
                                st.session_state.update_success_msg = f"✅ Task {selected_task_id} updated successfully!"
                                # Clear search and selection on successful update
                                st.session_state.task_id_search = ""
                                st.session_state.selected_task_id = None
                                st.cache_data.clear()
                                st.markdown("""
                                <script>
                                    window.parent.document.querySelector('[data-testid="stAppViewContainer"]').scrollTop = 0;
                                </script>
                                """, unsafe_allow_html=True)
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
