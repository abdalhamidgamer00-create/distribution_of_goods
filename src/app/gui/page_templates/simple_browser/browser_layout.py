"""Main rendering layout."""

import streamlit as st
import os
import typing
from src.app.gui.services.file_service import list_output_files
from src.app.gui.utils.translations import MESSAGES
from src.app.gui.page_templates.simple_browser import browser_setup as setup
from src.app.gui.page_templates.simple_browser import browser_filters as filters
from src.app.gui.page_templates.simple_browser import browser_rendering as rendering


def process_directory_tab(
    category: str,
    ext: str, 
    step_num: int, 
    key: str, 
    show_branch: bool
) -> None:
    """Process and render content using QueryOutputs use case."""
    from src.app.gui.services.pipeline_service import get_repository
    from src.application.use_cases.query_outputs import QueryOutputs
    
    repository = get_repository()
    use_case = QueryOutputs(repository)
    
    # Get all outputs for category
    files = use_case.execute(category)
    
    # Filter by extension
    files = [f for f in files if f['name'].endswith(ext)]
    
    if not files:
        st.info(MESSAGES["no_files"])
        return

    # Add relative_path key early for filters compatibility
    for f in files:
        if 'relative_path' not in f:
            f['relative_path'] = f['path']

    st.success(f"تم العثور على {len(files)} ملف")

    filtered_files = files
    if show_branch:
        filtered_files = filters.filter_files_by_branch(
            filtered_files, key, ext
        )
    
    filtered_files = filters.filter_files_by_category(
        filtered_files, key, ext
    )
    
    rendering.render_files_list(filtered_files, ext, key)


def render_simple_browser(
    title: str, 
    icon: str, 
    csv_dir: str, 
    excel_dir: str, 
    step: int, 
    key: str, 
    show_branch: bool = True,
    category: "typing.Optional[str]" = None
) -> None:
    """Render the main simple file browser using domain use cases."""
    if category is None:
        # Fallback to key if category not provided
        category = key.lower()

    setup.setup_page_config(title, icon)
    
    tabs = st.tabs(["📊 Excel", "📄 CSV"])
    extensions = [".xlsx", ".csv"]
    
    for tab, ext in zip(tabs, extensions):
        with tab:
            process_directory_tab(category, ext, step, key, show_branch)
