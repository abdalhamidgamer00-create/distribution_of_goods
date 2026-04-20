"""Page setup logic."""

import streamlit as st
from src.presentation.gui.utils.auth import check_password


def setup_page_config(title: str, icon: str, help_text: str = None) -> None:
    """Setup page header and authentication."""
    
    if not check_password():
        st.stop()
        
    st.title(f"{icon} {title}", help=help_text)
    st.markdown("---")
