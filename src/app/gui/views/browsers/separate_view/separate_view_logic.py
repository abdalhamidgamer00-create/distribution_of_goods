"""Logic for separate transfers view tabs."""

from typing import List, Dict
import streamlit as st
from src.app.gui.views.browsers.separate_view import (
    separate_view_filters as filters, 
    separate_view_display as display
)
from src.app.gui.services.pipeline_service import get_repository
from src.application.use_cases.query_outputs import QueryOutputs
def process_separate_tab(
    directory: str,
    extension: str,
    step_number: int,
    key_prefix: str,
    selected_branch: str
) -> None:
    """Processes single tab logic using QueryOutputs use case."""
    target_branch_id, category_id = filters.render_filters(key_prefix, extension)
    files = _load_and_filter_files(
        selected_branch, extension, target_branch_id, category_id
    )
    
    if not files:
        st.info("لا توجد ملفات")
        return
    if selected_branch == "all":
        _handle_all_branches_view(files, key_prefix, extension)
    else:
        _handle_single_branch_view(files, key_prefix, selected_branch, extension)
def _load_and_filter_files(
    selected_branch: str, extension: str, target: str, category: str
) -> List[Dict]:
    """Loads and applies initial filters to separate files."""
    repository = get_repository()
    use_case = QueryOutputs(repository)
    
    branch_query = None if selected_branch == "all" else selected_branch
    files = use_case.execute('separate', branch_query)
    
    # Filter by extension and add metadata
    prepared = []
    for file_info in files:
        if not file_info['name'].endswith(extension):
            continue
        if target and file_info.get('target_branch') != target:
            continue
        if category and category not in file_info.get('product_category', ''):
            continue
            
        file_info['relative_path'] = file_info.get(
            'relative_path', file_info['path']
        )
        file_info['source_branch'] = file_info.get('branch', selected_branch)
        prepared.append(file_info)
        
    return prepared
def _group_files_by_source(files: List[Dict]) -> Dict[str, List[Dict]]:
    """Helper to group files by their source branch."""
    grouped_files: Dict[str, List[Dict]] = {}
    for file_info in files:
        source_key = file_info.get('source_branch', 'عام')
        if source_key not in grouped_files:
            grouped_files[source_key] = []
        grouped_files[source_key].append(file_info)
    return grouped_files
def _handle_all_branches_view(
    files: List[Dict], key_prefix: str, extension: str
) -> None:
    """Groups files by source branch and dispatches to grouped display."""
    grouping_enabled = st.toggle(
        "تجميع حسب فرع المصدر", value=True, key=f"{key_prefix}_{extension.strip('.')}_toggle"
    )
    if grouping_enabled:
        grouped_files = _group_files_by_source(files)
    else:
        grouped_files = {"all": files}
    display.display_separate_files_grouped(
        grouped_files, files, key_prefix, extension
    )
def _handle_single_branch_view(
    files: List[Dict], key_prefix: str, selected_branch: str, extension: str
) -> None:
    """Displays separate files for a specific branch."""
    st.success(f"تم العثور على {len(files)} ملف")
    display.display_separate_files(
        files, key_prefix, selected_branch, extension
    )
