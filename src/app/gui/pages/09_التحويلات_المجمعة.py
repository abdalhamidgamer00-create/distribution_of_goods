"""صفحة التحويلات المجمعة - Merged"""

import streamlit as st
import os
import sys
import pandas as pd


# =============================================================================
# PATH CONFIGURATION
# =============================================================================

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app.gui.utils.file_manager import (
    list_output_files,
    read_file_for_display,
    create_download_zip,
    get_file_size_str
)
from src.app.gui.utils.translations import BRANCH_NAMES, CATEGORY_NAMES, MESSAGES
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

BRANCH_LABELS = {
    'admin': '🏢 الإدارة',
    'asherin': '🏪 العشرين',
    'wardani': '🏬 الوردانى',
    'akba': '🏭 العقبى',
    'shahid': '🏗️ الشهيد',
    'nujum': '⭐ النجوم'
}


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


def _get_category_key(selected_category: str) -> str:
    """Get category key from translated name."""
    if selected_category == "الكل":
        return None
    for key, value in CATEGORY_NAMES.items():
        if value == selected_category:
            return key
    return None


# =============================================================================
# RENDERING HELPERS
# =============================================================================

def _render_download_all_button(all_files: list, selected_branch: str, file_ext: str) -> None:
    """Render download all button."""
    zip_files = []
    for file_info in all_files:
        new_info = file_info.copy()
        new_info['zip_path'] = os.path.join(file_info.get('folder_name', ''), file_info['name'])
        zip_files.append(new_info)
    
    zip_name = f"combined_merged_{selected_branch}_{file_ext[1:]}.zip"
    zip_data = create_download_zip(zip_files, zip_name)
    st.download_button(
        label=f"📦 تحميل الملفات المعروضة ({len(all_files)})",
        data=zip_data,
        file_name=zip_name,
        mime="application/zip",
        use_container_width=True
    )
    st.markdown("---")


def _render_file_expander(file_info: dict, file_ext: str) -> None:
    """Render file expander with dataframe and download button."""
    with st.expander(f"📄 {file_info['name']} ({get_file_size_str(file_info['size'])})"):
        content_column, download_column = st.columns([3, 1])
        
        with content_column:
            dataframe = read_file_for_display(file_info['path'], max_rows=50)
            if dataframe is not None:
                st.dataframe(dataframe, use_container_width=True)
                st.caption("عرض أول 50 صف")
        
        with download_column:
            with open(file_info['path'], 'rb') as file_handle:
                file_data = file_handle.read()
            
            st.download_button(
                label="⬇️ تحميل",
                data=file_data,
                file_name=file_info['name'],
                mime="application/octet-stream",
                key=f"merged_download_{file_info['name']}_{file_ext}"
            )


def _group_files_by_branch(all_files: list) -> dict:
    """Group files by branch."""
    files_by_branch = {}
    for file_info in all_files:
        branch = file_info.get('branch', 'unknown')
        if branch not in files_by_branch:
            files_by_branch[branch] = []
        files_by_branch[branch].append(file_info)
    return files_by_branch


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

branches = get_branches()

# All branches button
if st.button("🌐 كل الفروع", key="merged_branch_btn_all", use_container_width=True):
    st.session_state['merged_selected_branch'] = 'all'

# Branch buttons in 3 columns
column_1, column_2, column_3 = st.columns(3)
columns = [column_1, column_2, column_3, column_1, column_2, column_3]

for branch_index, branch in enumerate(branches):
    with columns[branch_index]:
        if st.button(BRANCH_LABELS.get(branch, branch), key=f"merged_branch_btn_{branch}", use_container_width=True):
            st.session_state['merged_selected_branch'] = branch

# Show selected branch
if 'merged_selected_branch' in st.session_state:
    selected = st.session_state['merged_selected_branch']
    if selected == 'all':
        st.info("📂 عرض التحويلات المجمعة من: **كل الفروع**")
    else:
        st.info(f"📂 عرض التحويلات المجمعة من: **{BRANCH_LABELS.get(selected, selected)}**")
else:
    st.warning("⚠️ يرجى اختيار فرع من الأزرار أعلاه")

st.markdown("---")


# =============================================================================
# MAIN CONTENT
# =============================================================================

if 'merged_selected_branch' in st.session_state:
    selected_branch = st.session_state['merged_selected_branch']
    
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
                    category_key = _get_category_key(selected_category)
                    
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
                        _render_download_all_button(all_files, selected_branch, file_ext)
                    
                    # Group by branch for display
                    files_by_branch = _group_files_by_branch(all_files)
                    
                    for branch, files in files_by_branch.items():
                        branch_name = BRANCH_LABELS.get(branch, branch)
                        st.subheader(f"{branch_name}")
                        
                        for file_info in files:
                            _render_file_expander(file_info, file_ext)
                        
                        st.markdown("---")
