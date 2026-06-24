"""Tab processing logic for transfers view."""
from typing import List, Dict, Optional
import streamlit as st
from . import (
    transfers_view_filters as logic_filters, 
    transfers_view_display as display_interface
)
from src.presentation.gui.services.pipeline_service import get_repository
from src.application.use_cases.query_outputs import QueryOutputs
from src.shared.collections import group_by

def process_transfer_tab(
    target_directory: str,
    file_extension: str,
    processing_step_number: int,
    interaction_key_prefix: str,
    target_branch_name: str,
    available_branches_list: list
) -> None:
    """Processes single tab logic using QueryOutputs use case."""
    artifact_list = _load_and_prepare_files(target_branch_name, file_extension)
    
    if not artifact_list:
        st.warning("لا توجد ملفات")
        return

    if target_branch_name == "all":
        _handle_all_branches_view(
            artifact_list, interaction_key_prefix, file_extension
        )
    else:
        _handle_single_branch_view(
            artifact_list, 
            target_branch_name, 
            available_branches_list, 
            interaction_key_prefix, 
            file_extension
        )

def _load_and_prepare_files(
    target_branch_name: str, 
    file_extension: str, 
    report_category: str = 'transfers'
) -> List[Dict]:
    """Loads and prepares transfer files for the UI."""
    artifact_repository = get_repository()
    query_use_case = QueryOutputs(artifact_repository)
    
    branch_query_filter = (
        None if target_branch_name == "all" else target_branch_name
    )
    artifact_list = query_use_case.execute(report_category, branch_query_filter)
    
    # Filter by extension and add compatibility metadata
    prepared_artifact_list = []
    for artifact_info in artifact_list:
        if artifact_info['name'].endswith(file_extension):
            if 'relative_path' not in artifact_info:
                artifact_info['relative_path'] = artifact_info['path']
            prepared_artifact_list.append(artifact_info)
            
    return prepared_artifact_list

def _handle_all_branches_view(
    artifact_list: List[Dict], 
    interaction_key_prefix: str, 
    file_extension: str
) -> None:
    """Groups files by branch and dispatches to grouped display."""
    grouped_artifacts = group_by(
        artifact_list, key_func=lambda a: a.get('branch', 'عام')
    )
            
    display_interface.display_transfer_files_grouped(
        grouped_artifacts, artifact_list, interaction_key_prefix, file_extension
    )

def _handle_single_branch_view(
    artifact_list: List[Dict], 
    target_branch_name: str, 
    available_branches_list: list,
    interaction_key_prefix: str, 
    file_extension: str
) -> None:
    """Applies branch filters and dispatches to standard display."""
    filtered_artifacts = logic_filters.filter_transfers(
        artifact_list, 
        target_branch_name, 
        available_branches_list, 
        interaction_key_prefix, 
        file_extension
    )
    
    if filtered_artifacts:
        display_interface.display_transfer_files(
            filtered_artifacts, 
            interaction_key_prefix, 
            target_branch_name, 
            file_extension
        )

