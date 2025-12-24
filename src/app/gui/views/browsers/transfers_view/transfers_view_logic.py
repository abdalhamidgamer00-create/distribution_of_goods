"""Tab processing logic for transfers view."""

from typing import List, Dict, Optional
import streamlit as st
from src.app.gui.views.browsers.transfers_view import transfers_view_filters as filters
from src.app.gui.views.browsers.transfers_view import transfers_view_display as display
from src.app.gui.services.pipeline_service import get_repository
from src.application.use_cases.query_outputs import QueryOutputs

def process_transfer_tab(
    directory: str,
    extension: str,
    step_number: int,
    key_prefix: str,
    selected_branch: str,
    branches_list: list
) -> None:
    """
    Process single tab logic using QueryOutputs use case.
    
    Args:
        directory: The base directory for files
        extension: File extension to filter (.csv or .xlsx)
        step_number: The pipeline step number
        key_prefix: Unique prefix for UI element keys
        selected_branch: The selected branch label (or "الكل")
        branches_list: List of available branches
    """
    repository = get_repository()
    use_case = QueryOutputs(repository)
    
    # Handle "All Branches" selection
    is_all_branches = selected_branch == "all"
    branch_query = None if is_all_branches else selected_branch
    
    # Get transfer outputs
    files = use_case.execute('transfers', branch_query)
    
    # Filter by extension
    files = [f for f in files if f['name'].endswith(extension)]
    
    if not files:
        st.warning("لا توجد ملفات")
        return

    # Add relative_path key for compatibility with display
    for file_info in files:
        if 'relative_path' not in file_info:
            file_info['relative_path'] = file_info['path']

    if is_all_branches:
        # Group files by branch for the "All" view
        grouped_files: Dict[str, List[Dict]] = {}
        for file_info in files:
            branch_key = file_info.get('branch', 'عام')
            if branch_key not in grouped_files:
                grouped_files[branch_key] = []
            grouped_files[branch_key].append(file_info)
            
        display.display_transfer_files_grouped(
            grouped_files, 
            key_prefix, 
            extension
        )
    else:
        # Apply filters for specific branch view
        filtered_files = filters.filter_transfers(
            files, 
            selected_branch, 
            branches_list, 
            key_prefix, 
            extension
        )
        
        if filtered_files:
            display.display_transfer_files(
                filtered_files, 
                key_prefix, 
                selected_branch, 
                extension
            )
