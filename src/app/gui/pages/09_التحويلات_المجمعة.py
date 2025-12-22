"""صفحة التحويلات المجمعة - Merged"""

import streamlit as st
import os
import sys


# =============================================================================
# PATH CONFIGURATION
# =============================================================================

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app.gui.utils.file_manager import create_download_zip
from src.app.gui.utils.translations import CATEGORY_NAMES
from src.app.gui.utils.gui_components import (
    BRANCH_LABELS,
    render_branch_selection_buttons,
    render_selected_branch_info,
    render_file_expander,
    render_download_all_button,
    get_key_from_label,
    group_files_by_branch
)
from src.core.domain.branches.config import get_branches


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="التحويلات المجمعة",
    page_icon="📋",
    layout="wide"
)


# =============================================================================
# AUTHENTICATION
# =============================================================================

from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()


# =============================================================================
# CONSTANTS
# =============================================================================

MERGED_CSV_DIR = os.path.join("data", "output", "combined_transfers", "merged", "csv")
MERGED_EXCEL_DIR = os.path.join("data", "output", "combined_transfers", "merged", "excel")

SESSION_KEY = 'merged_selected_branch'


# =============================================================================
# FOLDER PARSING HELPERS
# =============================================================================

def _parse_folder_info(folder_name: str, folder_path: str) -> dict:
    """Parse folder name to extract branch information."""
    parts = folder_name.replace('combined_transfers_from_', '').split('_')
    branch = parts[0] if parts else 'unknown'
    return {'name': folder_name, 'path': folder_path, 'branch': branch}


def _matches_branch_filter(branch: str, branch_filter: str) -> bool:
    """Check if branch matches the filter."""
    return not branch_filter or branch_filter == 'all' or branch == branch_filter


def get_branch_folders(base_dir, branch_filter=None):
    """Get all branch folders with timestamps."""
    if not os.path.exists(base_dir):
        return []
    folders = []
    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        if os.path.isdir(folder_path) and folder_name.startswith('combined_transfers_from_'):
            info = _parse_folder_info(folder_name, folder_path)
            if _matches_branch_filter(info['branch'], branch_filter):
                folders.append(info)
    return folders


# =============================================================================
# FILE LISTING HELPERS
# =============================================================================

def _build_file_info(folder_path: str, filename: str) -> dict:
    """Build file info dict."""
    filepath = os.path.join(folder_path, filename)
    return {'name': filename, 'path': filepath, 'size': os.path.getsize(filepath), 'relative_path': filename}


def list_files_in_folder(folder_path, extensions):
    """List files in a folder."""
    if not os.path.exists(folder_path):
        return []
    return [_build_file_info(folder_path, filename) for filename in os.listdir(folder_path) 
            if any(filename.endswith(extension) for extension in extensions)]


# =============================================================================
# ZIP PREPARATION HELPERS
# =============================================================================

def _prepare_and_download(all_files: list, selected_branch: str, file_ext: str) -> None:
    """Prepare zip files and render download button."""
    zip_files = []
    for file_info in all_files:
        new_info = file_info.copy()
        new_info['zip_path'] = os.path.join(file_info.get('folder_name', ''), file_info['name'])
        zip_files.append(new_info)
    
    zip_name = f"combined_merged_{selected_branch}_{file_ext[1:]}.zip"
    render_download_all_button(zip_files, zip_name)


# =============================================================================
# PAGE HEADER
# =============================================================================

st.title("📋 التحويلات المجمعة (Merged)")
st.markdown("**جميع التحويلات من كل فرع في ملف واحد لكل فئة منتج**")
st.markdown("---")


# =============================================================================
# BRANCH SELECTION
# =============================================================================

st.subheader("📍 اختر الفرع المرسل")
st.caption("اختر فرع لعرض جميع تحويلاته المجمعة")

render_branch_selection_buttons(SESSION_KEY, "merged")

selected_branch = render_selected_branch_info(
    SESSION_KEY,
    "📂 عرض التحويلات المجمعة من: **{branch_name}**"
)

st.markdown("---")


# =============================================================================
# MAIN CONTENT
# =============================================================================

if selected_branch:
    excel_tab, csv_tab = st.tabs(["📊 ملفات Excel", "📄 ملفات CSV"])
    
    for tab, directory, file_ext in [(excel_tab, MERGED_EXCEL_DIR, ".xlsx"), (csv_tab, MERGED_CSV_DIR, ".csv")]:
        with tab:
            if not os.path.exists(directory):
                st.warning(f"المجلد غير موجود: {directory}")
                st.info("يرجى تشغيل الخطوة 11 أولاً لإنشاء ملفات التحويلات المجمعة")
            else:
                branch_folders = get_branch_folders(directory, selected_branch)
                
                if not branch_folders:
                    st.info("لا توجد ملفات بعد. يرجى تشغيل الخطوة 11 أولاً.")
                else:
                    # Category filter
                    category_options = ["الكل"] + list(CATEGORY_NAMES.values())
                    selected_category = st.selectbox("فلتر حسب الفئة:", category_options, key=f"merged_category_{file_ext}")
                    category_key = get_key_from_label(selected_category, CATEGORY_NAMES)
                    
                    # Collect all files
                    all_files = []
                    for folder_info in branch_folders:
                        files = list_files_in_folder(folder_info['path'], [file_ext])
                        for file_info in files:
                            file_info['branch'] = folder_info['branch']
                            file_info['folder_name'] = folder_info['name']
                        all_files.extend(files)
                    
                    # Filter by category
                    if category_key:
                        all_files = [file_info for file_info in all_files if category_key in file_info['name'].lower()]
                    
                    st.success(f"تم العثور على {len(all_files)} ملف")
                    
                    # Download and display
                    if all_files:
                        _prepare_and_download(all_files, selected_branch, file_ext)
                    
                    # Group by branch for display
                    files_by_branch = group_files_by_branch(all_files)
                    
                    for branch, files in files_by_branch.items():
                        branch_name = BRANCH_LABELS.get(branch, branch)
                        st.subheader(f"{branch_name}")
                        
                        for file_info in files:
                            render_file_expander(file_info, file_ext, key_prefix="merged")
                        
                        st.markdown("---")
