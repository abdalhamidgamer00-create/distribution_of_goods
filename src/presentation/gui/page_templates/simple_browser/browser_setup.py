"""Page setup logic."""

import streamlit as st
from src.presentation.gui.utils.auth import check_password


def setup_page_config(title: str, icon: str) -> None:
    """Setup page configuration and authentication."""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    
    if not check_password():
        st.stop()
        
    st.title(f"{icon} {title}")
    st.markdown("---")
