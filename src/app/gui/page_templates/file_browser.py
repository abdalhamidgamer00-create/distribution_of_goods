"""File browser template with common file listing and display logic."""
import streamlit as st
import os
from typing import List, Dict, Optional, Callable
from src.app.gui.components import (
    render_file_expander,
    render_download_all_button
)


# =============================================================================
# PUBLIC API
# =============================================================================

def build_file_info(folder_path: str, filename: str) -> dict:
    """Build file info dict."""
    filepath = os.path.join(folder_path, filename)
    return {
        'name': filename,
        'path': filepath,
        'size': os.path.getsize(filepath),
        'relative_path': filename
    }


def list_files_in_folder(
    folder_path: str,
    extensions: List[str]
) -> List[dict]:
    """List files in a folder with given extensions."""
    if not os.path.exists(folder_path):
        return []
        
    return [
        build_file_info(folder_path, filename)
        for filename in os.listdir(folder_path)
        if any(filename.endswith(ext) for ext in extensions)
    ]


def parse_folder_info(
    folder_name: str,
    folder_path: str, 
    prefix: str
) -> dict:
    """Parse folder name to extract branch information."""
    parts = folder_name.replace(prefix, '').split('_')
    branch = parts[0] if parts else 'unknown'
    return {
        'name': folder_name,
        'path': folder_path,
        'branch': branch
    }


def get_matching_folders(
    base_dir: str,
    prefix: str,
    branch_filter: Optional[str] = None
) -> List[dict]:
    """Get all folders matching prefix and optional branch filter."""
    if not os.path.exists(base_dir):
        return []
        
    folders = []
    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        
        if not (os.path.isdir(folder_path) and 
                folder_name.startswith(prefix)):
            continue
            
        info = parse_folder_info(folder_name, folder_path, prefix)
        
        if _is_branch_match(info['branch'], branch_filter):
            folders.append(info)
            
    return folders


def render_file_tabs(
    excel_dir: str,
    csv_dir: str,
    render_content_func: Callable
) -> None:
    """Render Excel and CSV tabs with content."""
    excel_tab, csv_tab = st.tabs(["📊 ملفات Excel", "📄 ملفات CSV"])
    
    tabs_data = [
        (excel_tab, excel_dir, ".xlsx"),
        (csv_tab, csv_dir, ".csv")
    ]
    
    for tab, directory, file_ext in tabs_data:
        with tab:
            render_content_func(directory, file_ext)


def render_files_with_download(
    files: List[dict],
    file_ext: str,
    zip_name: str,
    key_prefix: str,
    prepare_zip_func: Optional[Callable] = None
) -> None:
    """Render files list with download all button."""
    st.success(f"تم العثور على {len(files)} ملف")
    
    if files:
        zip_files = files
        if prepare_zip_func:
            zip_files = prepare_zip_func(files)
            
        render_download_all_button(zip_files, zip_name)
    
    for file_info in files:
        render_file_expander(file_info, file_ext, key_prefix=key_prefix)


# =============================================================================
# PRIVATE HELPERS
# =============================================================================

def _is_branch_match(
    branch: str,
    branch_filter: Optional[str]
) -> bool:
    """Check if branch matches filter."""
    if not branch_filter or branch_filter == 'all':
        return True
    return branch == branch_filter
