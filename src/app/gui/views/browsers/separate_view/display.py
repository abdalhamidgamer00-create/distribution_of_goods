"""File display logic for separate transfers view."""

import os
import streamlit as st
from src.app.gui.components import (
    BRANCH_LABELS,
    render_file_expander,
    render_download_all_button
)
from src.app.gui.services.file_service import group_files_by_source_target


def display_separate_files(
    files: list,
    kp: str,
    sel: str,
    ext: str
) -> None:
    """Display separate files grouped by source/target."""
    for f in files:
        f['zip_path'] = os.path.join(
            f['source_folder'], 
            f['target_folder'], 
            f['name']
        )
        
    render_download_all_button(files, f"{kp}_{sel}_{ext[1:]}.zip")
    
    grouped = group_files_by_source_target(files)
    for (s, t), fs in grouped.items():
        header = f"{BRANCH_LABELS.get(s, s)} ← {BRANCH_LABELS.get(t, t)}"
        st.subheader(header)
        
        for f in fs:
            render_file_expander(
                f, ext, key_prefix=f"{kp}_{s}_{t}"
            )
        st.markdown("---")
