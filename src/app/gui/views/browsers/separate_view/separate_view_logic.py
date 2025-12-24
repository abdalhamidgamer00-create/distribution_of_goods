"""Logic for separate transfers view tabs."""

from typing import List, Dict, Optional
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
    """
    Process single tab logic using QueryOutputs use case.
    
    Args:
        directory: The base directory for files
        extension: File extension to filter (.csv or .xlsx)
        step_number: The pipeline step number
        key_prefix: Unique prefix for UI element keys
        selected_branch: The selected branch key (or "all")
    """
    repository = get_repository()
    use_case = QueryOutputs(repository)
    
    target_branch_key, category_key = filters.render_filters(key_prefix, extension)
    
    # Handle "All Branches" selection
    is_all_branches = selected_branch == "all"
    branch_query = None if is_all_branches else selected_branch
    
    # Get all separate outputs
    files = use_case.execute('separate', branch_query)
    
    # Filter by extension, target, and category
    files = [f for f in files if f['name'].endswith(extension)]
    
    if target_branch_key:
        files = [f for f in files if f.get('target_branch') == target_branch_key]
    if category_key:
        files = [f for f in files if category_key in f.get('product_category', '')]
        
    if not files:
        st.info("لا توجد ملفات")
        return

    # Add extra keys for compatibility with display
    for file_info in files:
        if 'relative_path' not in file_info:
            file_info['relative_path'] = file_info['path']
        if 'source_branch' not in file_info:
            file_info['source_branch'] = file_info.get('branch', selected_branch)

    if is_all_branches:
        # Group files by source branch for the "All" view
        grouped_files: Dict[str, List[Dict]] = {}
        for file_info in files:
            source_key = file_info.get('source_branch', 'عام')
            if source_key not in grouped_files:
                grouped_files[source_key] = []
            grouped_files[source_key].append(file_info)
            
        display.display_separate_files_grouped(
            grouped_files, 
            files,
            key_prefix, 
            extension
        )
    else:
        # Specific branch view
        st.success(f"تم العثور على {len(files)} ملف")
        
        if files:
            display.display_separate_files(
                files, 
                key_prefix, 
                selected_branch, 
                extension
            )
