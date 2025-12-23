"""Main orchestration for branch selector."""

import streamlit as st
from typing import Optional
from src.app.gui.components.branch_selector.layout import render_buttons
from src.app.gui.components.branch_selector.display import render_selected_branch_info

def render_branch_selection_section(
    session_key: str,
    subheader_label: str,
    info_message_template: str,
    key_prefix: str = None
) -> Optional[str]:
    """Render complete branch selection section."""
    if key_prefix is None:
        key_prefix = session_key
        
    st.subheader(subheader_label)
    render_buttons(session_key, key_prefix)
    selected = render_selected_branch_info(session_key, info_message_template)
    st.markdown("---")
    
    return selected
