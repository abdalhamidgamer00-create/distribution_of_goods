"""Internal rendering logic for separate transfers view."""

import streamlit as st
from typing import List, Dict
from src.app.gui.components import (
    render_file_expander, 
    render_download_all_button
)
from src.app.gui.utils.translations import BRANCH_NAMES
from src.app.gui.services.file_service import group_files_by_source_target
from src.app.gui.utils.display_utils import (
    extract_clean_branch_name, 
    prepare_zip_paths
)


def render_grouped_separate_entries(
    files: List[Dict], 
    key_prefix: str, 
    extension: str
) -> None:
    """Renders separate entries grouped by source and target branches."""
    grouped = group_files_by_source_target(files)
    for (source, target), branch_files in grouped.items():
        clean_source = extract_clean_branch_name(source)
        clean_target = extract_clean_branch_name(target)
        header = (
            f"{BRANCH_NAMES.get(clean_source, source)} ← "
            f"{BRANCH_NAMES.get(clean_target, target)}"
        )
        st.subheader(header)
        
        for file_info in branch_files:
            render_file_expander(
                file_info, extension, 
                key_prefix=(
                    f"{key_prefix}_{clean_source}_"
                    f"{clean_target}_{extension}_expander"
                )
            )
        st.markdown("---")


def render_subgrouped_by_target(
    files: List[Dict], 
    clean_source: str, 
    key_prefix: str, 
    extension: str
) -> None:
    """Re-groups by target within a tab for better readability."""
    sub_grouped = group_files_by_source_target(files)
    for (source, target), branch_files in sub_grouped.items():
        clean_target = extract_clean_branch_name(target)
        header = f"إلى: {BRANCH_NAMES.get(clean_target, target)}"
        st.write(f"**{header}**")
        for file_info in branch_files:
            render_file_expander(
                file_info, extension, 
                key_prefix=(
                    f"{key_prefix}_tab_{clean_source}_"
                    f"{clean_target}_{extension}_expander"
                )
            )
        st.markdown("---")

def render_separate_tab_content(
    raw_key: str, 
    files: List[Dict], 
    key_prefix: str, 
    extension: str
) -> None:
    """Renders the content for single separate branch tab."""
    clean_key = extract_clean_branch_name(raw_key)
    branch_label = BRANCH_NAMES.get(clean_key, raw_key)
    
    st.subheader(f"الملفات المنفصلة من: {branch_label}")
    st.info(f"عدد الملفات: {len(files)}")
    
    prepare_zip_paths(files, path_strategy='nested')
    zip_filename = f"{key_prefix}_{clean_key}_{extension[1:]}.zip"
    render_download_all_button(
        files, zip_filename, 
        key=f"{key_prefix}_tab_{clean_key}_{extension}_btn"
    )
    
    render_subgrouped_by_target(files, clean_key, key_prefix, extension)
