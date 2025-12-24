"""Logic for merged view tabs."""

from typing import List, Dict
import streamlit as st
from src.presentation.gui.views.browsers.merged_view import (
    merged_view_filters as filters, 
    merged_view_display as display
)
from src.presentation.gui.services.pipeline_service import get_repository
from src.application.use_cases.query_outputs import QueryOutputs


def process_merged_tab(
    directory: str,
    extension: str,
    step_number: int,
    key_prefix: str,
    selected_branch: str
) -> None:
    """Processes single tab logic using QueryOutputs use case."""
    files = _load_and_prepare_files(selected_branch, extension)
    
    if not files:
        st.info("لا توجد ملفات")
        return

    if selected_branch == "all":
        _handle_all_branches_view(files, key_prefix, extension)
    else:
        _handle_single_branch_view(
            files, key_prefix, selected_branch, extension
        )


def _load_and_prepare_files(selected_branch: str, extension: str) -> List[Dict]:
    """Loads and prepares merged files for the UI."""
    repository = get_repository()
    use_case = QueryOutputs(repository)
    
    branch_query = None if selected_branch == "all" else selected_branch
    files = use_case.execute('merged', branch_query)
    
    # Filter by extension and add compatibility metadata
    prepared_files = []
    for file_info in files:
        if file_info['name'].endswith(extension):
            if 'relative_path' not in file_info:
                file_info['relative_path'] = file_info['path']
            prepared_files.append(file_info)
            
    return prepared_files


def _handle_all_branches_view(
    files: List[Dict], key_prefix: str, extension: str
) -> None:
    """Groups files by branch and dispatches to grouped display."""
    grouped_files: Dict[str, List[Dict]] = {}
    for file_info in files:
        branch_key = file_info.get('branch', 'عام')
        if branch_key not in grouped_files:
            grouped_files[branch_key] = []
        grouped_files[branch_key].append(file_info)
            
    display.display_merged_files_grouped(
        grouped_files, files, key_prefix, extension
    )


def _handle_single_branch_view(
    files: List[Dict], key_prefix: str, selected_branch: str, extension: str
) -> None:
    """Applies branch filters and dispatches to standard display."""
    from . import merged_view_filters as filters
    filtered_files = filters.filter_merged_files(
        files, key_prefix, extension
    )
    
    if filtered_files:
        display.display_merged_files(
            filtered_files, key_prefix, selected_branch, extension
        )
