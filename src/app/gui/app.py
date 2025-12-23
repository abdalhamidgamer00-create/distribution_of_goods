"""Main Streamlit Application."""
import streamlit as st
import os
import sys

# =============================================================================
# SETUP
# =============================================================================

# Path configuration
if __name__ == "__main__":
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../..')
    )
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# Page config
st.set_page_config(
    page_title="مشاريع صيدليات محروس", 
    page_icon="💊", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Auth
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()

# Imports after path setup
from src.app.gui.layout import render_sidebar, apply_custom_styles

# =============================================================================
# MAIN LAYOUT
# =============================================================================

apply_custom_styles()
render_sidebar()

# =============================================================================
# STATE MANAGEMENT
# =============================================================================

if "page" not in st.session_state:
    st.session_state.page = "home"
