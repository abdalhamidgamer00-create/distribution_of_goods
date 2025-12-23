"""Main rendering layout."""

import streamlit as st
import os
from src.app.gui.services.file_service import list_output_files
from src.app.gui.utils.translations import MESSAGES
from src.app.gui.page_templates.simple_browser import (
    setup, filters, rendering
)


def process_directory_tab(
    directory: str, 
    ext: str, 
    step_num: int, 
    key: str, 
    show_branch: bool
) -> None:
    """Process and render content for a single directory tab."""
    if not os.path.exists(directory):
        st.warning(f"يرجى تشغيل الخطوة {step_num} أولاً.")
        return

    files = list_output_files(directory, [ext])
    
    if not files:
        st.info(MESSAGES["no_files"])
        return

    st.success(f"تم العثور على {len(files)} ملف")

    filtered_files = files
    if show_branch:
        filtered_files = filters.filter_files_by_branch(filtered_files, key, ext)
    
    filtered_files = filters.filter_files_by_category(filtered_files, key, ext)
    
    rendering.render_files_list(filtered_files, ext, key)


def render_simple_browser(
    title: str, 
    icon: str, 
    csv_dir: str, 
    excel_dir: str, 
    step: int, 
    key: str, 
    show_branch: bool = True
) -> None:
    """Render the main simple file browser page structure."""
    setup.setup_page_config(title, icon)
    
    tabs = st.tabs(["📊 Excel", "📄 CSV"])
    directories = [excel_dir, csv_dir]
    extensions = [".xlsx", ".csv"]
    
    for tab, directory, ext in zip(tabs, directories, extensions):
        with tab:
            process_directory_tab(directory, ext, step, key, show_branch)
