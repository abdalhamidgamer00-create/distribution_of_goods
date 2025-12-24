"""Branch selection layout components."""

import streamlit as st
from src.core.domain.branches.config import get_branches
from src.app.gui.components.branch_selector.branch_selector_constants import BRANCH_LABELS

def render_grid_buttons(session_key: str, key_prefix: str) -> None:
    """Render the grid of branch buttons."""
    branches = get_branches()
    col1, col2, col3 = st.columns(3)
    columns = [col1, col2, col3, col1, col2, col3]
    
    for idx, branch in enumerate(branches):
        with columns[idx]:
            label = BRANCH_LABELS.get(branch, branch)
            key = f"{key_prefix}_branch_btn_{branch}"
            
            if st.button(label, key=key, use_container_width=True):
                st.session_state[session_key] = branch


def render_buttons(
    session_key: str,
    key_prefix: str,
    include_all: bool = True,
    all_button_label: str = "🌐 كل الفروع"
) -> None:
    """Render branch selection buttons in a 3-column layout."""
    if include_all:
        if st.button(
            all_button_label, 
            key=f"{key_prefix}_branch_btn_all", 
            use_container_width=True
        ):
            st.session_state[session_key] = 'all'
    
    render_grid_buttons(session_key, key_prefix)
