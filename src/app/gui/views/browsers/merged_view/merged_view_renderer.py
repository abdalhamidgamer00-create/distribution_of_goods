"""Internal rendering logic for merged view."""

import streamlit as st
from typing import List, Dict
from src.app.gui.components import render_file_expander
from src.app.gui.utils.translations import BRANCH_NAMES
from src.app.gui.services.file_service import group_files_by_branch
from src.app.gui.utils.display_utils import extract_clean_branch_name


def render_grouped_merged_files(
    files: List[Dict], 
    key_prefix: str, 
    extension: str
) -> None:
    """Renders files grouped by their internal branch keys."""
    grouped = group_files_by_branch(files)
    for raw_key, branch_files in grouped.items():
        clean_key = extract_clean_branch_name(raw_key)
        st.subheader(BRANCH_NAMES.get(clean_key, raw_key))
        for file_info in branch_files:
            render_file_expander(
                file_info, extension, 
                key_prefix=f"{key_prefix}_{clean_key}_{extension}_expander"
            )
        st.markdown("---")


def render_merged_files_list(
    files: List[Dict], 
    clean_key: str, 
    key_prefix: str, 
    extension: str
) -> None:
    """Renders a simple list of file expanders."""
    for file_info in files:
        render_file_expander(
            file_info, extension, 
            key_prefix=f"{key_prefix}_tab_{clean_key}_{extension}"
        )
