import streamlit as st
import pandas as pd
from utils import load_cora_data
from datetime import datetime
import requests

def get_cora_status():
    return "Active"

def get_cora_leads():
    try:
        df = load_cora_data()
        return df.to_dict('records') if not df.empty else []
    except:
        return []

def send_approved_leads_to_mark(lead_ids):
    """Send approved Lead IDs to MARK webhook"""
    webhook_url = "https://hackett2k.app.n8n.cloud/webhook/mark-approve-leads"
    
    payload = {
        "approved_leads": lead_ids,
        "approved_by": "Dashboard User",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 200, response
    except Exception as e:
        return False, str(e)

def cora_page():
    st.header("CORA - Lead Generation Dashboard")

    df = load_cora_data()

    if df.empty:
        st.info("No CORA data available.")
        return

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
    if not df.empty and 'Lead ID' in df.columns:
        with st.expander("📧 Approve Leads for Outreach", expanded=False):
            st.markdown("**Select leads to approve for MARK to send outreach emails**")
            
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
                if st.button("🔄 Refresh", use_container_width=True):
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
