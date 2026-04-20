"""Display logic for transfers view."""

import os
import re
from typing import List, Dict
import streamlit as st
from src.presentation.gui.components import (
    render_file_expander,
    render_download_all_button
)
from src.presentation.gui.utils.translations import BRANCH_NAMES

from src.presentation.gui.utils.display_utils import prepare_zip_paths


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
        files, zip_filename, 
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
    """Renders the global info and download button."""
    st.info(f"📂 عرض كلي لجميع الفروع ({len(all_files)} ملف)")
    prepare_zip_paths(all_files, path_strategy='transfer')
    zip_filename = f"{key_prefix}_all_branches_{extension[1:]}.zip"
    render_download_all_button(
        all_files, zip_filename,
        label_template="📦 تحميل جميع ملفات الفروع ({count})",
        key=f"{key_prefix}_global_all_btn_{extension}_all"
    )


def _render_branch_tab_content(
    branch_key: str, files: List[Dict], key_prefix: str, extension: str
) -> None:
    """Renders the content within a specific branch tab."""
    branch_label = BRANCH_NAMES.get(branch_key, branch_key)
    st.subheader(f"تحويلات من: {branch_label}")
    st.info(f"عدد الملفات: {len(files)}")
    prepare_zip_paths(files, path_strategy='transfer')
    zip_filename = f"{key_prefix}_{branch_key}_{extension[1:]}.zip"
    render_download_all_button(
        files, zip_filename, 
        key=f"{key_prefix}_tab_{branch_key}_{extension}_btn"
    )
    for i, file_info in enumerate(files):
        render_file_expander(
            file_info, extension, 
            key_prefix=f"{key_prefix}_tab_{branch_key}_{extension}_{i}"
        )


def display_collection_files(
    files: List[Dict],
    key_prefix: str,
    selected_branch: str,
    extension: str
) -> None:
    """Display collected files grouped by category for a premium look."""
    # 1. Group files by category extracted from filename
    # Pattern: from_[branch]_[category]_[timestamp]
    category_groups: Dict[str, List[Dict]] = {}
    
    for f in files:
        # Extract category: remove prefix 'from_[branch]_all_' and suffix '_[timestamp]'
        name = f['name']
        match = re.search(fr"from_{selected_branch}_all_(.+?)_\d+\.(csv|xlsx)", name)
        if match:
            cat = match.group(1).replace('_', ' ').title()
        else:
            cat = "عام / أخرى"
        
        if cat not in category_groups:
            category_groups[cat] = []
        category_groups[cat].append(f)

    # 2. Render Header & Metrics
    st.markdown(f"### 📊 ملخص التحويلات لفرع {selected_branch}")
    m1, m2 = st.columns(2)
    m1.metric("عدد التصنيفات", len(category_groups))
    m2.metric("إجمالي الملفات", len(files))
    st.markdown("---")

    # 3. Render Categorized Sections
    for cat, cat_files in category_groups.items():
        with st.container():
            st.markdown(f"#### 🏷️ قسم: {cat}")
            
            # Action: Download all for this category
            prepare_zip_paths(cat_files, path_strategy='transfer')
            zip_name = f"{key_prefix}_{selected_branch}_{cat.lower().replace(' ', '_')}.zip"
            render_download_all_button(
                cat_files, zip_name,
                label_template=f"📦 تحميل تصنيف {cat} ({{count}})",
                key=f"{key_prefix}_{selected_branch}_{cat}_{extension}_btn"
            )
            
            # File list
            for i, f in enumerate(cat_files):
                render_file_expander(
                    f, extension,
                    key_prefix=f"{key_prefix}_{cat}_{i}_{extension}"
                )
            st.markdown("<br>", unsafe_allow_html=True)
