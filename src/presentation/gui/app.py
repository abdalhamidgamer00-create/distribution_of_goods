import src.presentation.gui.page_setup  # noqa: F401  -- path bootstrap

import streamlit as st

# Page config (must be before any other streamlit calls)
st.set_page_config(
    page_title="مشاريع صيدليات محروس", 
    page_icon="💊", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Imports after path setup
from src.presentation.gui.layout.styles import apply_custom_styles
from src.presentation.gui.layout.sidebar import _render_info_box
from src.presentation.gui.services.navigation import get_navigation_config

# Apply premium styles early (so they affect the login page too)
apply_custom_styles()

# Auth
from src.presentation.gui.utils.auth import check_password
if not check_password():
    st.stop()

# =============================================================================
# NAVIGATION & SIDEBAR
# =============================================================================

# Define and run navigation
pg = st.navigation(get_navigation_config())

# Standard Sidebar Branding
with st.sidebar:
    st.markdown("## 💊 صيدليات محروس")
    st.markdown("---")

# Run current page
pg.run()
