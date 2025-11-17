import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import requests

# ========================================
# GOOGLE SHEETS CONNECTION
# ========================================

@st.cache_resource
def connect_to_sheets():
    """Connect to Google Sheets using service account credentials"""
    try:
        credentials_dict = dict(st.secrets["google_credentials"])
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scope)
        client = gspread.authorize(credentials)
        return client
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
        client = connect_to_sheets()
        if client:
            # Get CORA sheet ID from secrets or use default
            sheet_id = st.secrets.get("CORA_SHEET_ID", st.secrets.get("GOOGLE_SHEET_ID"))
            sheet = client.open_by_key(sheet_id).sheet1
            data = sheet.get_all_records()
            return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading CORA data: {e}")
        return pd.DataFrame()

# ========================================
# OPSI DATA FUNCTIONS
# ========================================

@st.cache_data(ttl=60)  # Cache for 1 minute
def load_opsi_data():
    """Load OPSI tasks from Google Sheets"""
    try:
        client = connect_to_sheets()
        if client:
            # OPSI sheet ID
            sheet_id = st.secrets.get("OPSI_SHEET_ID", "1kt4z_zcfiX_Xx3jhahihWMB5LMrh0-GpmQDBxKjSl4A")
            sheet = client.open_by_key(sheet_id).sheet1
            data = sheet.get_all_records()
            return pd.DataFrame(data)
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

# ========================================
# MARK WEBHOOK FUNCTIONS
# ========================================

def send_to_mark_webhook(payload):
    """Send data to MARK agent webhook"""
    webhook_url = "https://hackett2k.app.n8n.cloud/webhook/mark-approve-leads"
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        return response.status_code == 200, response
    except Exception as e:
        return False, str(e)
