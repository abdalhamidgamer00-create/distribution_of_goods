"""Page setup logic."""

import streamlit as st
from src.presentation.gui.utils.auth import check_password


def setup_page_config(title: str, icon: str) -> None:
    """Setup page header and authentication."""
    
    if not check_password():
        st.stop()
        
    st.title(f"{icon} {title}")
    st.markdown("---")
