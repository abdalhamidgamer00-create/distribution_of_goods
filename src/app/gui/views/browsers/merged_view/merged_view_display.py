"""Display logic for merged view."""

import os
from typing import List, Dict
import streamlit as st
from src.app.gui.components import (
    render_file_expander,
    render_download_all_button
)
from src.app.gui.utils.translations import BRANCH_NAMES
from src.app.gui.services.file_service import group_files_by_branch


def _prepare_zip_paths(files: List[Dict]) -> None:
    """Helper to prepare zip paths for merged files."""
    for file_info in files:
        file_info['zip_path'] = os.path.join(
            file_info.get('folder_name', ''), 
            file_info['name']
        )


def display_merged_files(
    files: List[Dict],
    key_prefix: str,
    selected_branch: str,
    extension: str
) -> None:
    """
    Display merged files grouped by branch.
    
    Args:
        files: List of file metadata dictionaries
        key_prefix: Unique prefix for UI element keys
        selected_branch: The selected branch key
        extension: File extension (.csv or .xlsx)
    """
    branch_label = BRANCH_NAMES.get(selected_branch, selected_branch)
    st.success(f"تم العثور على {len(files)} ملف لـ {branch_label}")
    
    _prepare_zip_paths(files)
        
    zip_name = f"{key_prefix}_{selected_branch}_{extension[1:]}.zip"
    render_download_all_button(
        files, 
        zip_name, 
        key=f"{key_prefix}_{selected_branch}_{extension}_download"
    )
    
    grouped = group_files_by_branch(files)
    for branch_key, branch_files in grouped.items():
        st.subheader(BRANCH_NAMES.get(branch_key, branch_key))
        for file_info in branch_files:
            render_file_expander(
                file_info, 
                extension, 
                key_prefix=f"{key_prefix}_{branch_key}_{extension}"
            )
        st.markdown("---")


def display_merged_files_grouped(
    grouped_files: Dict[str, List[Dict]],
    all_files: List[Dict],
    key_prefix: str,
    extension: str
) -> None:
    """
    Display merged files organized by branch using tabs.
    
    Args:
        grouped_files: Dictionary mapping branch keys to lists of files
        all_files: Flat list of all files across all branches
        key_prefix: Unique prefix for UI element keys
        extension: File extension (.csv or .xlsx)
    """
    st.info(f"📂 عرض كلي للملفات المجمعة ({len(all_files)} ملف)")
    
    _prepare_zip_paths(all_files)
    
    global_zip_name = f"{key_prefix}_all_merged_{extension[1:]}.zip"
    render_download_all_button(
        all_files, 
        global_zip_name,
        label_template="📦 تحميل جميع الملفات المجمعة ({count})",
        key=f"{key_prefix}_global_merged_btn_{extension}"
    )
    
    branch_keys = sorted(grouped_files.keys())
    tab_labels = [BRANCH_NAMES.get(k, k) for k in branch_keys]
    
    tabs = st.tabs(tab_labels)
    
    for branch_key, tab in zip(branch_keys, tabs):
        with tab:
            files = grouped_files[branch_key]
            branch_label = BRANCH_NAMES.get(branch_key, branch_key)
            
            st.subheader(f"الملفات المجمعة لـ: {branch_label}")
            st.info(f"عدد الملفات: {len(files)}")
            
            _prepare_zip_paths(files)
            
            zip_name = f"{key_prefix}_{branch_key}_{extension[1:]}.zip"
            render_download_all_button(
                files, 
                zip_name, 
                key=f"{key_prefix}_{branch_key}_{extension}_tab_download"
            )
            
            for file_info in files:
                render_file_expander(
                    file_info, 
                    extension, 
                    key_prefix=f"{key_prefix}_{branch_key}_{extension}_tab"
                )
