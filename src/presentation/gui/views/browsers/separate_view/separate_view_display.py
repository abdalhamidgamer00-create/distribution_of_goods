"""File display logic for separate transfers view."""

import os
import re
from typing import List, Dict
import streamlit as st
from src.presentation.gui.components import (
    render_file_expander,
    render_download_all_button
)
from src.presentation.gui.utils.translations import BRANCH_NAMES
from src.presentation.gui.services.file_service import group_files_by_source_target


from .separate_view_renderer import (
    render_grouped_separate_entries,
    render_subgrouped_by_target,
    render_separate_tab_content
)
from src.presentation.gui.utils.display_utils import (
    extract_clean_branch_name, 
    prepare_zip_paths
)


def display_separate_files(
    files: List[Dict],
    key_prefix: str,
    selected_branch: str,
    extension: str
) -> None:
    """Display separate files grouped by source/target."""
    prepare_zip_paths(files, path_strategy='nested')
        
    zip_filename = f"{key_prefix}_{selected_branch}_{extension[1:]}.zip"
    render_download_all_button(
        files, zip_filename, 
        key=f"{key_prefix}_{selected_branch}_{extension}_single_download"
    )
    
    render_grouped_separate_entries(files, key_prefix, extension)


def display_separate_files_grouped(
    grouped_files: Dict[str, List[Dict]],
    all_files: List[Dict],
    key_prefix: str,
    extension: str
) -> None:
    """Display separate files organized by source branch using tabs."""
    _render_global_separate_header(all_files, key_prefix, extension)
    
    raw_keys = sorted(grouped_files.keys())
    tab_labels = [
        BRANCH_NAMES.get(extract_clean_branch_name(k), k) 
        for k in raw_keys
    ]
    tabs = st.tabs(tab_labels)
    
    for raw_key, tab in zip(raw_keys, tabs):
        with tab:
            render_separate_tab_content(
                raw_key, grouped_files[raw_key], 
                key_prefix, extension
            )


def _render_global_separate_header(
    all_files: List[Dict], key_prefix: str, extension: str
) -> None:
    """Renders the global header and download all button."""
    st.info(f"📂 عرض كلي للملفات المنفصلة ({len(all_files)} ملف)")
    prepare_zip_paths(all_files, path_strategy='nested')
    
    zip_filename = f"{key_prefix}_all_separate_{extension[1:]}.zip"
    render_download_all_button(
        all_files, 
        zip_filename,
        label_template="📦 تحميل جميع الملفات المنفصلة ({count})",
        key=f"{key_prefix}_global_sep_btn_{extension}_all"
    )


