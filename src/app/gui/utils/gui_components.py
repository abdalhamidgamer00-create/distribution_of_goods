"""Shared GUI components for Streamlit pages."""

import streamlit as st
import os
from typing import Callable, Optional

from src.app.gui.utils.file_manager import (
    read_file_for_display,
    create_download_zip,
    get_file_size_str
)
from src.core.domain.branches.config import get_branches


# =============================================================================
# CONSTANTS
# =============================================================================

BRANCH_LABELS = {
    'admin': '🏢 الإدارة',
    'asherin': '🏪 العشرين',
    'wardani': '🏬 الورداني',
    'akba': '🏭 العقبي',
    'shahid': '🏗️ الشهيد',
    'nujum': '⭐ النجوم'
}


# =============================================================================
# KEY LOOKUP HELPERS
# =============================================================================

def get_key_from_label(label: str, labels_dict: dict) -> Optional[str]:
    """Get key from translated label.
    
    Args:
        label: The translated label to look up
        labels_dict: Dictionary mapping keys to labels
        
    Returns:
        The key if found, None otherwise
    """
    if label == "الكل":
        return None
    for key, value in labels_dict.items():
        if value == label:
            return key
    return None


def get_branch_key_from_label(selected_label: str) -> Optional[str]:
    """Get branch key from selected label.
    
    Args:
        selected_label: The selected branch label
        
    Returns:
        The branch key if found, None otherwise
    """
    return get_key_from_label(selected_label, BRANCH_LABELS)


# =============================================================================
# BRANCH SELECTION COMPONENTS
# =============================================================================

def render_branch_selection_buttons(
    session_key: str,
    key_prefix: str,
    include_all: bool = True,
    all_button_label: str = "🌐 كل الفروع"
) -> None:
    """Render branch selection buttons in a 3-column layout.
    
    Args:
        session_key: Session state key to store selected branch
        key_prefix: Prefix for button keys (e.g., 'merged', 'sep')
        include_all: Whether to include 'All branches' button
        all_button_label: Label for the 'All' button
    """
    branches = get_branches()
    
    # All branches button
    if include_all:
        if st.button(all_button_label, key=f"{key_prefix}_branch_btn_all", use_container_width=True):
            st.session_state[session_key] = 'all'
    
    # Branch buttons in 3 columns
    column_1, column_2, column_3 = st.columns(3)
    columns = [column_1, column_2, column_3, column_1, column_2, column_3]
    
    for branch_index, branch in enumerate(branches):
        with columns[branch_index]:
            if st.button(BRANCH_LABELS.get(branch, branch), key=f"{key_prefix}_branch_btn_{branch}", use_container_width=True):
                st.session_state[session_key] = branch


def render_selected_branch_info(
    session_key: str,
    message_template: str = "📂 عرض من: **{branch_name}**"
) -> Optional[str]:
    """Render selected branch info and return selected value.
    
    Args:
        session_key: Session state key containing selected branch
        message_template: Message template with {branch_name} placeholder
        
    Returns:
        The selected branch key, or None if not selected
    """
    if session_key in st.session_state:
        selected = st.session_state[session_key]
        if selected == 'all':
            st.info(message_template.format(branch_name="كل الفروع"))
        else:
            st.info(message_template.format(branch_name=BRANCH_LABELS.get(selected, selected)))
        return selected
    else:
        st.warning("⚠️ يرجى اختيار فرع من الأزرار أعلاه")
        return None


# =============================================================================
# FILE DISPLAY COMPONENTS
# =============================================================================

def render_file_expander(
    file_info: dict,
    file_ext: str,
    key_prefix: str = "download",
    show_row_count: bool = True,
    max_rows: int = 50
) -> None:
    """Render file expander with dataframe preview and download button.
    
    Args:
        file_info: Dict with 'name', 'path', 'size' keys
        file_ext: File extension (e.g., '.csv', '.xlsx')
        key_prefix: Prefix for download button key
        show_row_count: Whether to show row count caption
        max_rows: Maximum rows to display in preview
    """
    with st.expander(f"📄 {file_info['name']} ({get_file_size_str(file_info['size'])})"):
        content_column, download_column = st.columns([3, 1])
        
        with content_column:
            dataframe = read_file_for_display(file_info['path'], max_rows=max_rows)
            if dataframe is not None:
                st.dataframe(dataframe, use_container_width=True)
                if show_row_count:
                    st.caption(f"عرض أول {max_rows} صف")
        
        with download_column:
            with open(file_info['path'], 'rb') as file_handle:
                file_data = file_handle.read()
            
            st.download_button(
                label="⬇️ تحميل",
                data=file_data,
                file_name=file_info['name'],
                mime="application/octet-stream",
                key=f"{key_prefix}_{file_info['name']}_{file_ext}"
            )


def render_download_all_button(
    files: list,
    zip_name: str,
    label_template: str = "📦 تحميل الملفات المعروضة ({count})",
    add_separator: bool = True
) -> None:
    """Render download all button for a list of files.
    
    Args:
        files: List of file info dicts (must have 'zip_path' key prepared)
        zip_name: Name of the zip file
        label_template: Button label template with {count} placeholder
        add_separator: Whether to add markdown separator after button
    """
    if not files:
        return
    
    zip_data = create_download_zip(files, zip_name)
    st.download_button(
        label=label_template.format(count=len(files)),
        data=zip_data,
        file_name=zip_name,
        mime="application/zip",
        use_container_width=True
    )
    
    if add_separator:
        st.markdown("---")


# =============================================================================
# FILE GROUPING HELPERS
# =============================================================================

def group_files_by_branch(files: list, branch_key: str = 'branch') -> dict:
    """Group files by branch.
    
    Args:
        files: List of file info dicts
        branch_key: Key in file info dict containing branch name
        
    Returns:
        Dict mapping branch names to lists of files
    """
    files_by_branch = {}
    for file_info in files:
        branch = file_info.get(branch_key, 'unknown')
        if branch not in files_by_branch:
            files_by_branch[branch] = []
        files_by_branch[branch].append(file_info)
    return files_by_branch


def group_files_by_source_target(files: list) -> dict:
    """Group files by source and target branches.
    
    Args:
        files: List of file info dicts with 'source_branch' and 'target_branch' keys
        
    Returns:
        Dict mapping (source, target) tuples to lists of files
    """
    files_grouped = {}
    for file_info in files:
        source = file_info.get('source_branch', 'unknown')
        target = file_info.get('target_branch', 'unknown')
        key = (source, target)
        if key not in files_grouped:
            files_grouped[key] = []
        files_grouped[key].append(file_info)
    return files_grouped
