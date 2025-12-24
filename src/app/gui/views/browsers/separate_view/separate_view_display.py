"""File display logic for separate transfers view."""

import os
from typing import List, Dict
import streamlit as st
from src.app.gui.components import (
    render_file_expander,
    render_download_all_button
)
from src.app.gui.utils.translations import BRANCH_NAMES
from src.app.gui.services.file_service import group_files_by_source_target


def _prepare_zip_paths(files: List[Dict]) -> None:
    """Helper to prepare zip paths for separate files."""
    for file_info in files:
        file_info['zip_path'] = os.path.join(
            file_info.get('source_folder', 'unknown'), 
            file_info.get('target_folder', 'unknown'), 
            file_info['name']
        )


def display_separate_files(
    files: List[Dict],
    key_prefix: str,
    selected_branch: str,
    extension: str
) -> None:
    """
    Display separate files grouped by source/target.
    
    Args:
        files: List of file metadata dictionaries
        key_prefix: Unique prefix for UI element keys
        selected_branch: The selected branch key
        extension: File extension (.csv or .xlsx)
    """
    _prepare_zip_paths(files)
        
    zip_name = f"{key_prefix}_{selected_branch}_{extension[1:]}.zip"
    render_download_all_button(
        files, 
        zip_name, 
        key=f"{key_prefix}_{selected_branch}_{extension}_download"
    )
    
    grouped = group_files_by_source_target(files)
    for (source, target), branch_files in grouped.items():
        header = f"{BRANCH_NAMES.get(source, source)} ← {BRANCH_NAMES.get(target, target)}"
        st.subheader(header)
        
        for file_info in branch_files:
            render_file_expander(
                file_info, 
                extension, 
                key_prefix=f"{key_prefix}_{source}_{target}_{extension}"
            )
        st.markdown("---")


def display_separate_files_grouped(
    grouped_files: Dict[str, List[Dict]],
    all_files: List[Dict],
    key_prefix: str,
    extension: str
) -> None:
    """
    Display separate files organized by source branch using tabs.
    
    Args:
        grouped_files: Dictionary mapping source branch keys to lists of files
        all_files: Flat list of all files across all branches
        key_prefix: Unique prefix for UI element keys
        extension: File extension (.csv or .xlsx)
    """
    st.info(f"📂 عرض كلي للملفات المنفصلة ({len(all_files)} ملف)")
    
    _prepare_zip_paths(all_files)
    
    global_zip_name = f"{key_prefix}_all_separate_{extension[1:]}.zip"
    render_download_all_button(
        all_files, 
        global_zip_name,
        label_template="📦 تحميل جميع الملفات المنفصلة ({count})",
        key=f"{key_prefix}_global_sep_btn_{extension}"
    )
    
    branch_keys = sorted(grouped_files.keys())
    tab_labels = [BRANCH_NAMES.get(k, k) for k in branch_keys]
    
    tabs = st.tabs(tab_labels)
    
    for branch_key, tab in zip(branch_keys, tabs):
        with tab:
            files = grouped_files[branch_key]
            branch_label = BRANCH_NAMES.get(branch_key, branch_key)
            
            st.subheader(f"الملفات المنفصلة من: {branch_label}")
            st.info(f"عدد الملفات: {len(files)}")
            
            _prepare_zip_paths(files)
            
            zip_name = f"{key_prefix}_{branch_key}_{extension[1:]}.zip"
            render_download_all_button(
                files, 
                zip_name, 
                key=f"{key_prefix}_{branch_key}_{extension}_tab_download"
            )
            
            # Re-group by target for better readability within the tab
            sub_grouped = group_files_by_source_target(files)
            for (source, target), branch_files in sub_grouped.items():
                header = f"إلى: {BRANCH_NAMES.get(target, target)}"
                st.write(f"**{header}**")
                for file_info in branch_files:
                    render_file_expander(
                        file_info, 
                        extension, 
                        key_prefix=f"{key_prefix}_{branch_key}_{target}_{extension}_tab"
                    )
                st.markdown("---")
