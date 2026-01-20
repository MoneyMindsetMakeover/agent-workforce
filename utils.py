import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import requests
from datetime import datetime

# ========================================
# GOOGLE SHEETS CONNECTION
# ========================================

@st.cache_resource
def connect_to_sheets():
    """Connect to Google Sheets using service account credentials"""
    try:
        # Build credentials dict from flat structure
        credentials_dict = {
            "type": st.secrets["type"],
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": st.secrets["private_key"],
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": st.secrets["auth_uri"],
            "token_uri": st.secrets["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["client_x509_cert_url"]
        }
        
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
# DAPHNE DATA FUNCTIONS (MMM Donor Prospecting)
# ========================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_daphne_data():
    """Load DAPHNE donor prospects from Google Sheets"""
    try:
        client = connect_to_sheets()
        if client:
            # Get DAPHNE sheet ID from secrets
            sheet_id = st.secrets["DAPHNE_SHEET_ID"]
            sheet = client.open_by_key(sheet_id).sheet1
            data = sheet.get_all_records()
            return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading DAPHNE data: {e}")
        return pd.DataFrame()

def send_approved_leads_to_diana(donor_ids):
    """Send approved Donor IDs to DIANA webhook"""
    # Use MMM-specific webhook
    webhook_url = st.secrets.get(
        "DIANA_APPROVAL_WEBHOOK", 
        "https://infomoneymindsetmakeover.app.n8n.cloud/webhook/daphne-approve-leads"
    )
    
    payload = {
        "approved_donors": donor_ids,
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
        client = connect_to_sheets()
        if client:
            # OPSI sheet ID
            sheet_id = st.secrets["OPSI_SHEET_ID"]
            sheet = client.open_by_key(sheet_id).sheet1
            data = sheet.get_all_records()
            return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error loading OPSI data: {e}")
        return pd.DataFrame()

def send_opsi_task(task_data):
    """Send new OPSI task to n8n webhook"""
    # Use MMM-specific webhook
    webhook_url = st.secrets.get(
        "OPSI_CREATE_WEBHOOK", 
        "https://infomoneymindsetmakeover.app.n8n.cloud/webhook/opsi-create-task"
    )
    
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
    # Use MMM-specific webhook
    webhook_url = st.secrets.get(
        "OPSI_UPDATE_WEBHOOK", 
        "https://infomoneymindsetmakeover.app.n8n.cloud/webhook/opsi-update-task"
    )
    
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
