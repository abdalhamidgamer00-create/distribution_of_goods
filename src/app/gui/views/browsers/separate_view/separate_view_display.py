"""File display logic for separate transfers view."""

import os
import re
from typing import List, Dict
import streamlit as st
from src.app.gui.components import (
    render_file_expander,
    render_download_all_button
)
from src.app.gui.utils.translations import BRANCH_NAMES
from src.app.gui.services.file_service import group_files_by_source_target


def _extract_branch_name(branch_key: str) -> str:
    """
    Extract a clean branch key from potential folder names.
    e.g. 'combined_transfers_from_admin_20251224_082047' -> 'admin'
    """
    match = re.search(r'from_([a-z]+)_', branch_key)
    if match:
        return match.group(1)
    return branch_key


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
        key=f"{key_prefix}_{selected_branch}_{extension}_single_download"
    )
    
    grouped = group_files_by_source_target(files)
    for (source, target), branch_files in grouped.items():
        clean_source = _extract_branch_name(source)
        clean_target = _extract_branch_name(target)
        header = f"{BRANCH_NAMES.get(clean_source, source)} ← {BRANCH_NAMES.get(clean_target, target)}"
        st.subheader(header)
        
        for file_info in branch_files:
            render_file_expander(
                file_info, 
                extension, 
                key_prefix=f"{key_prefix}_{clean_source}_{clean_target}_{extension}_expander"
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
        key=f"{key_prefix}_global_sep_btn_{extension}_all"
    )
    
    raw_branch_keys = sorted(grouped_files.keys())
    tab_labels = []
    clean_keys = []
    
    for k in raw_branch_keys:
        clean_k = _extract_branch_name(k)
        tab_labels.append(BRANCH_NAMES.get(clean_k, k))
        clean_keys.append(clean_k)
    
    tabs = st.tabs(tab_labels)
    
    for raw_key, clean_key, tab in zip(raw_branch_keys, clean_keys, tabs):
        with tab:
            files = grouped_files[raw_key]
            branch_label = BRANCH_NAMES.get(clean_key, raw_key)
            
            st.subheader(f"الملفات المنفصلة من: {branch_label}")
            st.info(f"عدد الملفات: {len(files)}")
            
            _prepare_zip_paths(files)
            
            zip_name = f"{key_prefix}_{clean_key}_{extension[1:]}.zip"
            render_download_all_button(
                files, 
                zip_name, 
                key=f"{key_prefix}_tab_{clean_key}_{extension}_btn"
            )
            
            # Re-group by target for better readability within the tab
            sub_grouped = group_files_by_source_target(files)
            for (source, target), branch_files in sub_grouped.items():
                clean_target = _extract_branch_name(target)
                header = f"إلى: {BRANCH_NAMES.get(clean_target, target)}"
                st.write(f"**{header}**")
                for file_info in branch_files:
                    render_file_expander(
                        file_info, 
                        extension, 
                        key_prefix=f"{key_prefix}_tab_{clean_key}_{clean_target}_{extension}_expander"
                    )
                st.markdown("---")
