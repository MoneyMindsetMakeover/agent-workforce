import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import io

# ========================================
# GOOGLE SHEETS CONNECTION (PUBLIC SHEETS)
# ========================================

def get_sheet_id_from_url(url):
    """Extract sheet ID from Google Sheets URL"""
    if '/d/' in url:
        return url.split('/d/')[1].split('/')[0]
    return url

@st.cache_data(ttl=300)
def read_public_gsheet(sheet_url):
    """Read data from a public Google Sheet"""
    try:
        # Extract sheet ID
        sheet_id = get_sheet_id_from_url(sheet_url)
        
        # Export as CSV using Google Sheets export API
        export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        
        response = requests.get(export_url)
        response.raise_for_status()
        
        # Read CSV data into DataFrame
        df = pd.read_csv(io.StringIO(response.text))
        return df
    except Exception as e:
        st.error(f"❌ Error reading Google Sheet: {e}")
        return pd.DataFrame()

# ========================================
# CORA DATA FUNCTIONS
# ========================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_cora_data():
    """Load CORA leads from Google Sheets"""
    try:
        if "CORA_SHEET_URL" in st.secrets:
            sheet_url = st.secrets["CORA_SHEET_URL"]
            df = read_public_gsheet(sheet_url)
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
        if "OPSI_SHEET_URL" in st.secrets:
            sheet_url = st.secrets["OPSI_SHEET_URL"]
            df = read_public_gsheet(sheet_url)
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
