# =============================================================================
# SETUP (PATH CONFIGURATION)
# =============================================================================

import os
import sys

# Ensure project root is in sys.path for absolute imports starting with 'src'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st

# Page config
st.set_page_config(
    page_title="مشاريع صيدليات محروس", 
    page_icon="💊", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Auth
from src.presentation.gui.utils.auth import check_password
if not check_password():
    st.stop()

# Imports after path setup
from src.presentation.gui.layout import render_sidebar, apply_custom_styles

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
