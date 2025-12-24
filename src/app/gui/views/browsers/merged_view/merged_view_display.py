"""Display logic for merged view."""

import os

import re
from typing import List, Dict
import streamlit as st
from src.app.gui.components import (
    render_file_expander, render_download_all_button
)
from src.app.gui.utils.translations import BRANCH_NAMES
from src.app.gui.services.file_service import group_files_by_branch
from .merged_view_renderer import (
    render_grouped_merged_files, render_merged_files_list
)
from src.app.gui.utils.display_utils import (
    extract_clean_branch_name, prepare_zip_paths
)
def display_merged_files(
    files: List[Dict],
    key_prefix: str,
    selected_branch: str,
    extension: str
) -> None:
    """Display merged files grouped by branch."""
    branch_label = BRANCH_NAMES.get(selected_branch, selected_branch)
    st.success(f"تم العثور على {len(files)} ملف لـ {branch_label}")
    
    prepare_zip_paths(files, path_strategy='flat')
    zip_filename = f"{key_prefix}_{selected_branch}_{extension[1:]}.zip"
    render_download_all_button(
        files, zip_filename, 
        key=f"{key_prefix}_{selected_branch}_{extension}_single_download"
    )
    
    render_grouped_merged_files(files, key_prefix, extension)
def display_merged_files_grouped(
    grouped_files: Dict[str, List[Dict]],
    all_files: List[Dict],
    key_prefix: str,
    extension: str
) -> None:
    """Display merged files organized by branch using tabs."""
    _render_global_merged_header(all_files, key_prefix, extension)
    
    raw_keys = sorted(grouped_files.keys())
    tab_labels = [
        BRANCH_NAMES.get(extract_clean_branch_name(k), k) 
        for k in raw_keys
    ]
    tabs = st.tabs(tab_labels)
    
    for raw_key, tab in zip(raw_keys, tabs):
        with tab:
            _render_merged_tab_content(
                raw_key, grouped_files[raw_key], 
                key_prefix, extension
            )
def _render_global_merged_header(
    all_files: List[Dict], key_prefix: str, extension: str
) -> None:
    """Renders the global header for all merged files."""
    st.info(f"📂 عرض كلي للملفات المجمعة ({len(all_files)} ملف)")
    prepare_zip_paths(all_files, path_strategy='flat')
    
    zip_filename = f"{key_prefix}_all_merged_{extension[1:]}.zip"
    render_download_all_button(
        all_files, 
        zip_filename,
        label_template="📦 تحميل جميع الملفات المجمعة ({count})",
        key=f"{key_prefix}_global_merged_btn_{extension}_all"
    )
def _render_merged_tab_content(
    raw_key: str, 
    files: List[Dict], 
    key_prefix: str, 
    extension: str
) -> None:
    """Renders the content for a single merged branch tab."""
    clean_key = extract_clean_branch_name(raw_key)
    branch_label = BRANCH_NAMES.get(clean_key, raw_key)
    
    st.subheader(f"الملفات المجمعة لـ: {branch_label}")
    st.info(f"عدد الملفات: {len(files)}")
    
    prepare_zip_paths(files, path_strategy='flat')
    zip_filename = f"{key_prefix}_{clean_key}_{extension[1:]}.zip"
    render_download_all_button(
        files, zip_filename, 
        key=f"{key_prefix}_tab_{clean_key}_{extension}_btn"
    )
    
    render_merged_files_list(files, clean_key, key_prefix, extension)
