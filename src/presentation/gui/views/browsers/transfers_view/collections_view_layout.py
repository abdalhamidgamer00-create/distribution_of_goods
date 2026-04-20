"""Specialized dashboard layout for collection files."""
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

def render_collections_browser(
    display_title: str,
    browser_icon: str,
    comma_separated_values_directory: str,
    excel_spreadsheet_directory: str,
    processing_step_number: int,
    state_session_key: str,
    interaction_key_prefix: str,
    informative_help_text: str = None
) -> None:
    """Renders a premium collections browser with sidebar navigation."""
    
    if not setup_browser_page(
        display_title, browser_icon, informative_help_text
    ):
        return
        
    # 1. Sidebar Navigation (UX Improvement)
    with st.sidebar:
        st.markdown("### 📍 تصفية الفروع")
        st.info("اختر الفرع المصدر لعرض التقارير المجمعة الخاصة به.")
        render_branch_selection_buttons(
            state_session_key, 
            f"{interaction_key_prefix}_sidebar"
        )
        st.markdown("---")
        st.caption("نظام التجميعات الذكي - v1.0")

    # 2. State Resolution
    selected_branch = st.session_state.get(state_session_key, "all")
    
    # 3. Main Dashboard Rendering
    render_browser_tabs(
        comma_separated_values_directory,
        excel_spreadsheet_directory,
        lambda dir_path, extension: _process_collection_tab(
            selected_branch, extension, interaction_key_prefix
        )
    )

def _process_collection_tab(
    branch_name: str, 
    file_extension: str, 
    interaction_key_prefix: str
) -> None:
    """Bridge function to load files and call the premium display."""
    
    # Use refactored logic with correct parameter naming
    artifact_files = logic_layer._load_and_prepare_files(
        branch_name, 
        file_extension, 
        report_category='collections'
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
            interaction_key_prefix, 
            file_extension
        )
    else:
        display_layer.display_collection_files(
            artifact_files, 
            interaction_key_prefix, 
            branch_name, 
            file_extension
        )
