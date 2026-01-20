import streamlit as st
import pandas as pd
from utils import load_daphne_data

def get_daphne_status():
    """Return DAPHNE agent status"""
    return "Active"

def get_daphne_leads():
    """Get DAPHNE donor prospects as list of dictionaries"""
    try:
        df = load_daphne_data()
        return df.to_dict('records') if not df.empty else []
    except:
        return []
