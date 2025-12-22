"""صفحة ملفات التحويل"""

import streamlit as st
import os
import sys
import re


# =============================================================================
# PATH CONFIGURATION
# =============================================================================

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app.gui.utils.file_manager import list_output_files, create_download_zip
from src.app.gui.utils.gui_components import (
    BRANCH_LABELS,
    render_branch_selection_buttons,
    render_selected_branch_info,
    render_file_expander,
    render_download_all_button,
    get_branch_key_from_label
)
from src.core.domain.branches.config import get_branches


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="ملفات التحويل",
    page_icon="📤",
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

TRANSFERS_CSV_DIR = os.path.join("data", "output", "transfers", "csv")
TRANSFERS_EXCEL_DIR = os.path.join("data", "output", "transfers", "excel")

SESSION_KEY = 'selected_source_branch'


# =============================================================================
# FILE COLLECTION HELPERS
# =============================================================================

def _get_branch_folder_name(branch: str, file_ext: str) -> str:
    """Get folder name for branch based on file extension."""
    if file_ext == ".csv":
        return f"transfers_from_{branch}_to_other_branches"
    return f"transfers_excel_from_{branch}_to_other_branches"


def _collect_files_for_branch(directory: str, branch: str, file_ext: str) -> list:
    """Collect files for a specific branch."""
    branch_folder = _get_branch_folder_name(branch, file_ext)
    branch_path = os.path.join(directory, branch_folder)
    
    if os.path.exists(branch_path):
        return list_output_files(branch_path, [file_ext])
    return []


def _collect_all_branch_files(directory: str, branches: list, file_ext: str) -> list:
    """Collect files for all branches."""
    all_files = []
    for branch in branches:
        all_files.extend(_collect_files_for_branch(directory, branch, file_ext))
    return all_files


def _filter_files_by_target(all_files: list, target_key: str) -> list:
    """Filter files by target branch."""
    filtered_files = []
    for file_info in all_files:
        if f"to_{target_key}" in file_info['relative_path'] or f"to_{target_key}" in file_info['name']:
            filtered_files.append(file_info)
    return filtered_files


# =============================================================================
# ZIP PREPARATION HELPERS
# =============================================================================

def _extract_folder_name(file_info: dict) -> str:
    """Extract folder name from file info for zip organization."""
    relative_path = file_info['relative_path']
    parent_dir = os.path.dirname(relative_path)
    
    match = re.search(r'(from_[a-zA-Z0-9]+_to_[a-zA-Z0-9]+)', parent_dir)
    if match:
        return match.group(1)
    
    match_file = re.search(r'(from_[a-zA-Z0-9]+_to_[a-zA-Z0-9]+)', file_info['name'])
    if match_file:
        return match_file.group(1)
    
    return parent_dir if parent_dir else "other"


def _prepare_zip_files(filtered_files: list) -> list:
    """Prepare files with zip paths for download."""
    zip_files = []
    for file_info in filtered_files:
        folder_name = _extract_folder_name(file_info)
        new_info = file_info.copy()
        new_info['zip_path'] = os.path.join(folder_name, file_info['name'])
        zip_files.append(new_info)
    return zip_files


def _prepare_and_download(filtered_files: list, selected_branch: str, target_key: str, file_ext: str) -> None:
    """Prepare zip files and render download button."""
    zip_files = _prepare_zip_files(filtered_files)
    
    if target_key:
        zip_name = f"transfers_{selected_branch}_to_{target_key}_{file_ext[1:]}.zip"
    else:
        zip_name = f"transfers_{selected_branch}_to_all_{file_ext[1:]}.zip"
    
    render_download_all_button(zip_files, zip_name)


# =============================================================================
# PAGE HEADER
# =============================================================================

st.title("📤 ملفات التحويل")
st.markdown("---")


# =============================================================================
# BRANCH SELECTION
# =============================================================================

st.subheader("📍 اختر الفرع المصدر")
st.caption("اختر فرع لعرض جميع التحويلات منه إلى الفروع الأخرى")

render_branch_selection_buttons(SESSION_KEY, "transfers")

selected_branch = render_selected_branch_info(
    SESSION_KEY,
    "📂 عرض التحويلات من: **{branch_name}** → الفروع الأخرى"
)

st.markdown("---")


# =============================================================================
# MAIN CONTENT
# =============================================================================

if selected_branch:
    branches = get_branches()
    
    excel_tab, csv_tab = st.tabs(["📊 ملفات Excel", "📄 ملفات CSV"])
    
    for tab, directory, file_ext in [(excel_tab, TRANSFERS_EXCEL_DIR, ".xlsx"), (csv_tab, TRANSFERS_CSV_DIR, ".csv")]:
        with tab:
            if not os.path.exists(directory):
                st.warning(f"المجلد غير موجود: {directory}")
                st.info("يرجى تشغيل الخطوة 7 أولاً لإنشاء ملفات التحويل")
            else:
                # Collect files
                if selected_branch == 'all':
                    all_files = _collect_all_branch_files(directory, branches, file_ext)
                else:
                    all_files = _collect_files_for_branch(directory, selected_branch, file_ext)
                
                if not all_files:
                    if selected_branch == 'all':
                        st.warning("لا توجد ملفات تحويل لأي فرع")
                    else:
                        st.warning(f"لا توجد تحويلات من {BRANCH_LABELS.get(selected_branch, selected_branch)}")
                        st.info("قد لا يكون هناك فائض في هذا الفرع للتحويل")
                else:
                    # Target filter
                    if selected_branch == 'all':
                        target_options = ["الكل"] + [BRANCH_LABELS.get(branch, branch) for branch in branches]
                    else:
                        target_options = ["الكل"] + [BRANCH_LABELS.get(branch, branch) for branch in branches if branch != selected_branch]
                    
                    selected_target = st.selectbox("عرض التحويلات إلى:", target_options, key=f"target_filter_{file_ext}")
                    
                    # Filter files
                    if selected_target == "الكل":
                        filtered_files = all_files
                        target_key = None
                    else:
                        target_key = get_branch_key_from_label(selected_target)
                        filtered_files = _filter_files_by_target(all_files, target_key)
                    
                    st.success(f"تم العثور على {len(filtered_files)} ملف تحويل")
                    
                    # Download and display
                    if filtered_files:
                        _prepare_and_download(filtered_files, selected_branch, target_key, file_ext)
                    
                    for file_info in filtered_files:
                        render_file_expander(file_info, file_ext, key_prefix="transfers")
