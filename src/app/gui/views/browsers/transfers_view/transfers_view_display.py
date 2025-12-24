"""Display logic for transfers view."""

import os
import re
from typing import List, Dict
import streamlit as st
from src.app.gui.components import (
    render_file_expander,
    render_download_all_button
)
from src.app.gui.utils.translations import BRANCH_NAMES

def _prepare_zip_paths(files: List[Dict]) -> None:
    """Helper to prepare zip paths for a list of files."""
    for file_info in files:
        # Extract folder name for better zip structure
        match = re.search(
            r'(from_\w+_to_\w+)', 
            file_info.get('relative_path', '') + file_info['name']
        )
        file_info['zip_path'] = os.path.join(
            match.group(1) if match else 'other', 
            file_info['name']
        )

def display_transfer_files(
    files: List[Dict],
    key_prefix: str,
    selected_branch: str,
    extension: str
) -> None:
    """
    Display collected transfer files for a single branch.
    
    Args:
        files: List of file metadata dictionaries
        key_prefix: Unique prefix for UI element keys
        selected_branch: The selected branch label
        extension: File extension (.csv or .xlsx)
    """
    st.success(f"تم العثور على {len(files)} ملف لـ {selected_branch}")
    
    _prepare_zip_paths(files)
        
    zip_name = f"{key_prefix}_{selected_branch}_{extension[1:]}.zip"
    render_download_all_button(
        files, 
        zip_name, 
        key=f"{key_prefix}_{selected_branch}_{extension}"
    )
    
    for file_info in files:
        render_file_expander(file_info, extension, key_prefix=key_prefix)

def display_transfer_files_grouped(
    grouped_files: Dict[str, List[Dict]],
    all_files: List[Dict],
    key_prefix: str,
    extension: str
) -> None:
    """
    Display transfer files organized by branch using tabs.
    
    Args:
        grouped_files: Dictionary mapping branch keys to lists of files
        all_files: Flat list of all files across all branches
        key_prefix: Unique prefix for UI element keys
        extension: File extension (.csv or .xlsx)
    """
    st.info(f"📂 عرض كلي لجميع الفروع ({len(all_files)} ملف)")
    
    _prepare_zip_paths(all_files)
    
    global_zip_name = f"{key_prefix}_all_branches_{extension[1:]}.zip"
    render_download_all_button(
        all_files, 
        global_zip_name,
        label_template="📦 تحميل جميع ملفات الفروع ({count})",
        key=f"{key_prefix}_global_all_btn_{extension}"
    )
    
    branch_keys = sorted(grouped_files.keys())
    tab_labels = [BRANCH_NAMES.get(k, k) for k in branch_keys]
    
    tabs = st.tabs(tab_labels)
    
    for branch_key, tab in zip(branch_keys, tabs):
        with tab:
            files = grouped_files[branch_key]
            branch_label = BRANCH_NAMES.get(branch_key, branch_key)
            
            st.subheader(f"تحويلات من: {branch_label}")
            st.info(f"عدد الملفات: {len(files)}")
            
            _prepare_zip_paths(files)
            
            zip_name = f"{key_prefix}_{branch_key}_{extension[1:]}.zip"
            render_download_all_button(
                files, 
                zip_name, 
                key=f"{key_prefix}_{branch_key}_{extension}"
            )
            
            for file_info in files:
                render_file_expander(
                    file_info, 
                    extension, 
                    key_prefix=f"{key_prefix}_{branch_key}"
                )
