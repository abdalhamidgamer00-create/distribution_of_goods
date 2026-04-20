"""Generalized premium dashboard layout for all purchasing reports."""
import streamlit as st
from src.presentation.gui.components import (
    render_branch_selection_buttons,
    setup_browser_page,
    render_browser_tabs,
    group_files_by_branch
)
from src.presentation.gui.views.browsers.transfers_view import (
    transfers_view_logic as logic_layer
)
from src.presentation.gui.views.browsers.transfers_view import (
    transfers_view_display as display_layer
)

def render_premium_browser(
    display_title: str,
    browser_icon: str,
    comma_separated_values_directory: str,
    excel_spreadsheet_directory: str,
    processing_step_number: int,
    state_session_key: str,
    interaction_key_prefix: str,
    report_category_type: str,
    informative_help_text: str = None
) -> None:
    """Renders a premium dashboard browser with sidebar navigation."""
    
    if not setup_browser_page(
        display_title, browser_icon, informative_help_text
    ):
        return
        
    # 1. Sidebar Navigation (UX Improvement)
    with st.sidebar:
        st.markdown("### 📍 تصفية الفروع")
        st.info(
            f"اختر الفرع المصدر لعرض تقارير **{display_title}** الخاصة به."
        )
        render_branch_selection_buttons(
            state_session_key, 
            f"{interaction_key_prefix}_sidebar"
        )
        st.markdown("---")
        st.caption(f"نظام {display_title} الذكي - v1.2")

    # 2. State Resolution
    selected_source_branch = st.session_state.get(state_session_key, "all")
    
    # 3. Main Dashboard Rendering
    render_browser_tabs(
        comma_separated_values_directory,
        excel_spreadsheet_directory,
        lambda dir_path, extension: _process_premium_rendering_tab(
            selected_source_branch, 
            extension, 
            interaction_key_prefix, 
            report_category_type
        )
    )

def _process_premium_rendering_tab(
    branch_name: str, 
    file_extension: str, 
    key_prefix: str, 
    category_name: str
) -> None:
    """Bridge function to load files and call the premium display."""
    artifact_files = logic_layer._load_and_prepare_files(
        branch_name, 
        file_extension, 
        category=category_name
    )
    
    if not artifact_files:
        display_name = "كل الفروع" if branch_name == "all" else branch_name
        st.warning(
            f"⚠️ لا توجد ملفات متوفرة لـ **{display_name}** "
            f"بصيغة هذا التبويب."
        )
        return
    
    if branch_name == "all":
        grouped_files = group_files_by_branch(artifact_files)
        display_layer.display_collection_files_grouped(
            grouped_files, 
            artifact_files, 
            key_prefix, 
            file_extension
        )
    else:
        display_layer.display_collection_files(
            artifact_files, 
            key_prefix, 
            branch_name, 
            file_extension
        )

