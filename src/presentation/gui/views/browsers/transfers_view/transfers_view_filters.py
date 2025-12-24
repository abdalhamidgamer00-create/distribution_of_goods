"""Filtering logic for transfers view."""

from typing import List, Dict
import streamlit as st
from src.presentation.gui.components import (
    BRANCH_LABELS,
    get_branch_key_from_label
)


def filter_transfers(
    files: List[Dict],
    selected_branch: str,
    branches_list: list,
    key_prefix: str,
    extension: str
) -> List[Dict]:
    """
    Filter transfer files by target branch.
    
    Args:
        files: List of file metadata dictionaries
        selected_branch: The source branch label
        branches_list: List of available branch keys
        key_prefix: Unique prefix for UI element keys
        extension: File extension (.csv or .xlsx)
        
    Returns:
        Filtered list of files
    """
    options = ["الكل"] + [
        BRANCH_LABELS.get(branch_key, branch_key) 
        for branch_key in branches_list 
        if selected_branch == 'all' or branch_key != selected_branch
    ]
    
    selected_target = st.selectbox(
        "إلى:", 
        options, 
        key=f"{key_prefix}_target_{extension}"
    )
    target_branch_key = get_branch_key_from_label(selected_target)
    
    if not target_branch_key:
        return files
        
    return [
        f for f in files 
        if f"to_{target_branch_key}" in f['relative_path'] + f['name']
    ]
