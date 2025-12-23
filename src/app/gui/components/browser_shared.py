"""Shared browser components."""
import streamlit as st
from typing import Callable, Any
from src.app.gui.components.branch_selection import (
    render_branch_selection_buttons,
    render_selected_branch_info
)

def setup_browser_page(title: str, icon: str) -> bool:
    """Initialize page, check auth, and render header. Returns success."""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    
    from src.app.gui.utils.auth import check_password
    if not check_password():
        st.stop()
        return False
        
    st.title(f"{icon} {title}")
    st.markdown("---")
    return True

def handle_branch_selection(
    session_key: str,
    subheader_label: str = "📍 اختر الفرع",
    info_template: str = "📂 عرض من: **{branch_name}**"
) -> str:
    """Render branch selection and return selected branch key."""
    st.subheader(subheader_label)
    
    render_branch_selection_buttons(session_key, session_key)
    selected = render_selected_branch_info(session_key, info_template)
    st.markdown("---")
    
    return selected

def render_browser_tabs(
    csv_dir: str,
    excel_dir: str,
    content_callback: Callable[[str, str], Any]
) -> None:
    """Render Excel and CSV tabs and call callback for content."""
    tabs = st.tabs(["📊 Excel", "📄 CSV"])
    dirs = [excel_dir, csv_dir]
    exts = [".xlsx", ".csv"]

    for tab, d, ext in zip(tabs, dirs, exts):
        with tab:
            content_callback(d, ext)
