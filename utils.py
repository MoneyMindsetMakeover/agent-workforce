import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import requests
from datetime import datetime

# ========================================
# GOOGLE SHEETS CONNECTION
# ========================================

@st.cache_resource
def get_gsheets_connection():
    """Get Google Sheets connection using Streamlit's built-in connector"""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn
    except Exception as e:
        st.error(f"❌ Google Sheets connection error: {e}")
        return None

# ========================================
# CORA DATA FUNCTIONS
# ========================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_cora_data():
    """Load CORA leads from Google Sheets"""
    try:
        conn = get_gsheets_connection()
        if conn:
            # Get CORA sheet ID from secrets
            sheet_url = st.secrets.get("CORA_SHEET_URL", "")
            if sheet_url:
                df = conn.read(spreadsheet=sheet_url, ttl=300)
                return df
            else:
                st.warning("⚠️ CORA_SHEET_URL not found in secrets")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading CORA data: {e}")
        return pd.DataFrame()

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

# ========================================
# OPSI DATA FUNCTIONS
# ========================================

@st.cache_data(ttl=60)  # Cache for 1 minute
def load_opsi_data():
    """Load OPSI tasks from Google Sheets"""
    try:
        conn = get_gsheets_connection()
        if conn:
            # Get OPSI sheet URL from secrets
            sheet_url = st.secrets.get("OPSI_SHEET_URL", "")
            if sheet_url:
                df = conn.read(spreadsheet=sheet_url, ttl=60)
                return df
            else:
                st.warning("⚠️ OPSI_SHEET_URL not found in secrets")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading OPSI data: {e}")
        return pd.DataFrame()

def send_opsi_task(task_data):
    """Send new OPSI task to n8n webhook"""
    webhook_url = "https://hackett2k.app.n8n.cloud/webhook/opsi-create-task"
    
    try:
        response = requests.post(webhook_url, json=task_data, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ OPSI webhook error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"❌ Error sending OPSI task: {e}")
        return None

def update_opsi_task(update_data):
    """Update existing OPSI task via n8n webhook"""
    webhook_url = "https://hackett2k.app.n8n.cloud/webhook/opsi-update-task"
    
    try:
        response = requests.post(webhook_url, json=update_data, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ OPSI update webhook error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"❌ Error updating OPSI task: {e}")
        return None
