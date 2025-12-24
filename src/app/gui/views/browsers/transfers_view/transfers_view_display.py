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

from src.app.gui.utils.display_utils import prepare_zip_paths


def display_transfer_files(
    files: List[Dict],
    key_prefix: str,
    selected_branch: str,
    extension: str
) -> None:
    """Display collected transfer files for a single branch."""
    st.success(f"تم العثور على {len(files)} ملف لـ {selected_branch}")
    
    prepare_zip_paths(files, path_strategy='transfer')
        
    zip_filename = f"{key_prefix}_{selected_branch}_{extension[1:]}.zip"
    render_download_all_button(
        files, 
        zip_filename, 
        key=f"{key_prefix}_{selected_branch}_{extension}_single_download"
    )
    
    for file_info in files:
        render_file_expander(
            file_info, extension, 
            key_prefix=f"{key_prefix}_{extension}_expander"
        )


def display_transfer_files_grouped(
    grouped_files: Dict[str, List[Dict]],
    all_files: List[Dict],
    key_prefix: str,
    extension: str
) -> None:
    """Display transfer files organized by branch using tabs."""
    _render_global_transfer_header(all_files, key_prefix, extension)
    
    branch_keys = sorted(grouped_files.keys())
    tab_labels = [BRANCH_NAMES.get(k, k) for k in branch_keys]
    tabs = st.tabs(tab_labels)
    
    for branch_key, tab in zip(branch_keys, tabs):
        with tab:
            _render_branch_tab_content(
                branch_key, grouped_files[branch_key], 
                key_prefix, extension
            )


def _render_global_transfer_header(
    all_files: List[Dict], key_prefix: str, extension: str
) -> None:
    """Renders the global info and download button for all branches."""
    st.info(f"📂 عرض كلي لجميع الفروع ({len(all_files)} ملف)")
    prepare_zip_paths(all_files, path_strategy='transfer')
    
    zip_filename = f"{key_prefix}_all_branches_{extension[1:]}.zip"
    render_download_all_button(
        all_files, 
        zip_filename,
        label_template="📦 تحميل جميع ملفات الفروع ({count})",
        key=f"{key_prefix}_global_all_btn_{extension}_all"
    )


def _render_branch_tab_content(
    branch_key: str, 
    files: List[Dict], 
    key_prefix: str, 
    extension: str
) -> None:
    """Renders the content within a specific branch tab."""
    branch_label = BRANCH_NAMES.get(branch_key, branch_key)
    st.subheader(f"تحويلات من: {branch_label}")
    st.info(f"عدد الملفات: {len(files)}")
    
    prepare_zip_paths(files, path_strategy='transfer')
    zip_filename = f"{key_prefix}_{branch_key}_{extension[1:]}.zip"
    
    render_download_all_button(
        files, 
        zip_filename, 
        key=f"{key_prefix}_tab_{branch_key}_{extension}_btn"
    )
    
    for file_info in files:
        render_file_expander(
            file_info, extension, 
            key_prefix=f"{key_prefix}_tab_{branch_key}_{extension}"
        )
