"""Specialized dashboard layout for collection files."""
import streamlit as st
from src.presentation.gui.components import (
    render_branch_selection_buttons,
    setup_browser_page,
    render_browser_tabs
)
from src.presentation.gui.views.browsers.transfers_view import transfers_view_logic as logic
from src.presentation.gui.views.browsers.transfers_view import transfers_view_display as display

def render_collections_browser(
    title: str,
    icon: str,
    csv_directory: str,
    excel_directory: str,
    step_number: int,
    session_key: str,
    key_prefix: str,
    help_text: str = None
) -> None:
    """Renders a premium collections browser with sidebar navigation and grouping."""
    
    if not setup_browser_page(title, icon, help_text):
        return
        
    # 1. Sidebar Navigation (UX Improvement)
    with st.sidebar:
        st.markdown("### 📍 تصفية الفروع")
        st.info("اختر الفرع المصدر لعرض التقارير المجمعة الخاصة به.")
        render_branch_selection_buttons(session_key, f"{key_prefix}_sidebar")
        st.markdown("---")
        st.caption("نظام التجميعات الذكي - v1.0")

    # 2. State Resolution
    selected_branch = st.session_state.get(session_key, "all")
    
    if selected_branch == "all":
        st.info("👋 **مرحباً بك!** يرجى اختيار فرع محدد من **القائمة الجانبية** لمراجعة تجميعات التحويلات الخاصة به.")
        st.image("https://img.freemarket.com/v1/group-files.png", width=300) # Optional aesthetic placeholder
        return

    # 3. Main Dashboard Rendering
    render_browser_tabs(
        csv_directory,
        excel_directory,
        lambda dir_path, ext: _process_collection_tab(
            selected_branch, ext, key_prefix
        )
    )

def _process_collection_tab(branch: str, ext: str, key_prefix: str):
    """Bridge function to load files and call the premium display."""
    # We use the internal logic helper from transfers_view_logic
    files = logic._load_and_prepare_files(branch, ext)
    if not files:
        st.warning(f"⚠️ لا توجد ملفات متوفرة لفرع **{branch}** بصيغة هذا التبويب.")
        return
    
    display.display_collection_files(files, key_prefix, branch, ext)
