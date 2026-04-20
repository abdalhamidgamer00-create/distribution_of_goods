"""Logic for displaying individual transfer listings."""
import streamlit as streamlit_interface
from typing import List, Dict
from src.presentation.gui.components import (
    render_file_expander,
    render_download_all_button
)
from src.presentation.gui.utils.translations import BRANCH_NAMES
from src.presentation.gui.utils.display_utils import prepare_zip_paths

def display_individual_transfer_files(
    artifact_list: List[Dict],
    interaction_key_prefix: str,
    target_branch: str,
    file_extension: str
) -> None:
    """Display collected transfer files for a single branch."""
    streamlit_interface.success(
        f"تم العثور على {len(artifact_list)} ملف لـ {target_branch}"
    )
    
    prepare_zip_paths(artifact_list, path_strategy='transfer')
    zip_filename = (
        f"{interaction_key_prefix}_{target_branch}_"
        f"{file_extension[1:]}.zip"
    )
    
    render_download_all_button(
        artifact_list, 
        zip_filename, 
        key=f"{interaction_key_prefix}_{target_branch}_"
            f"{file_extension}_single_download"
    )
    
    for index, file_info in enumerate(artifact_list):
        render_file_expander(
            file_info, 
            file_extension, 
            key_prefix=f"{interaction_key_prefix}_{file_extension}_"
                       f"expander_{index}"
        )
