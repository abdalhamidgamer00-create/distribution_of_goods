"""Display logic for merged view."""

import os
import streamlit as st
from src.app.gui.components import (
    BRANCH_LABELS,
    render_file_expander,
    render_download_all_button
)
from src.app.gui.services.file_service import group_files_by_branch


def display_merged_files(
    files: list,
    kp: str,
    sel: str,
    ext: str
) -> None:
    """Display merged files grouped by branch."""
    for f in files:
        f['zip_path'] = os.path.join(
            f.get('folder_name', ''), 
            f['name']
        )
        
    render_download_all_button(files, f"{kp}_{sel}_{ext[1:]}.zip")
    
    grouped = group_files_by_branch(files)
    for b, fs in grouped.items():
        st.subheader(BRANCH_LABELS.get(b, b))
        for f in fs:
            render_file_expander(f, ext, key_prefix=kp)
        st.markdown("---")
