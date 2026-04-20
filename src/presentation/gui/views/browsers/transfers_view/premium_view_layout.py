"""Generalized premium dashboard layout for all purchasing reports."""
import streamlit as st
from src.presentation.gui.components import (
    render_branch_selection_buttons,
    setup_browser_page,
    render_browser_tabs,
    group_files_by_branch
)
from src.presentation.gui.views.browsers.transfers_view import transfers_view_logic as logic
from src.presentation.gui.views.browsers.transfers_view import transfers_view_display as display

def render_premium_browser(
    title: str,
    icon: str,
    csv_directory: str,
    excel_directory: str,
    step_number: int,
    session_key: str,
    key_prefix: str,
    category: str,
    help_text: str = None
) -> None:
    """Renders a premium dashboard browser with sidebar navigation and grouping."""
    
    if not setup_browser_page(title, icon, help_text):
        return
        
    # 1. Sidebar Navigation (UX Improvement)
    with st.sidebar:
        st.markdown("### 📍 تصفية الفروع")
        st.info(f"اختر الفرع المصدر لعرض تقارير **{title}** الخاصة به.")
        render_branch_selection_buttons(session_key, f"{key_prefix}_sidebar")
        st.markdown("---")
        st.caption(f"نظام {title} الذكي - v1.1")

    # 2. State Resolution
    selected_branch = st.session_state.get(session_key, "all")
    
    # 3. Main Dashboard Rendering
    render_browser_tabs(
        csv_directory,
        excel_directory,
        lambda dir_path, ext: _process_premium_tab(
            selected_branch, ext, key_prefix, category
        )
    )

def _process_premium_tab(branch: str, ext: str, key_prefix: str, category: str):
    """Bridge function to load files and call the premium display."""
    files = logic._load_and_prepare_files(branch, ext, category=category)
    
    if not files:
        branch_name = "كل الفروع" if branch == "all" else branch
        st.warning(f"⚠️ لا توجد ملفات متوفرة لـ **{branch_name}** بصيغة هذا التبويب.")
        return
    
    if branch == "all":
        # Group files for the global view
        grouped = group_files_by_branch(files)
        # Use specialized grouped display for collections, or generic for others
        if category == 'collections':
            display.display_collection_files_grouped(grouped, files, key_prefix, ext)
        else:
            # For other categories, we can use a similar grouped display
            # We'll adapt transfers_view_display to handle this
            display.display_collection_files_grouped(grouped, files, key_prefix, ext)
    else:
        # Direct display for single branch
        if category == 'collections':
            display.display_collection_files(files, key_prefix, branch, ext)
        else:
            # Fallback to collection-style display for consistency, 
            # or specialized logic for 'transfers'
            display.display_collection_files(files, key_prefix, branch, ext)
