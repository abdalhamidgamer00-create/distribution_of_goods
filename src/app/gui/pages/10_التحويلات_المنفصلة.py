"""صفحة التحويلات المنفصلة - Separate"""

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
    page_title="التحويلات المنفصلة",
    page_icon="📂",
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

SEPARATE_CSV_DIR = os.path.join("data", "output", "combined_transfers", "separate", "csv")
SEPARATE_EXCEL_DIR = os.path.join("data", "output", "combined_transfers", "separate", "excel")

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

def _parse_source_info(folder_name: str, folder_path: str) -> dict:
    """Parse source folder name to extract branch information."""
    parts = folder_name.replace('transfers_from_', '').split('_')
    branch = parts[0] if parts else 'unknown'
    return {'name': folder_name, 'path': folder_path, 'branch': branch}


def _matches_source_filter(branch: str, branch_filter: str) -> bool:
    """Check if source branch matches the filter."""
    return not branch_filter or branch_filter == 'all' or branch == branch_filter


def get_source_folders(base_dir, branch_filter=None):
    """Get all source branch folders with timestamps."""
    if not os.path.exists(base_dir):
        return []
    folders = []
    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        if os.path.isdir(folder_path) and folder_name.startswith('transfers_from_'):
            info = _parse_source_info(folder_name, folder_path)
            if _matches_source_filter(info['branch'], branch_filter):
                folders.append(info)
    return folders


def _build_target_folder_info(folder_path: str, folder_name: str) -> dict:
    """Build target folder info dict."""
    target = folder_name.replace('to_', '')
    return {'name': folder_name, 'path': folder_path, 'target': target}


def get_target_folders(source_folder_path):
    """Get all target branch folders within a source folder."""
    if not os.path.exists(source_folder_path):
        return []
    
    folders = []
    for folder_name in os.listdir(source_folder_path):
        folder_path = os.path.join(source_folder_path, folder_name)
        if os.path.isdir(folder_path) and folder_name.startswith('to_'):
            folders.append(_build_target_folder_info(folder_path, folder_name))
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


def _get_key_from_label(label: str, labels_dict: dict) -> str:
    """Get key from translated label."""
    if label == "الكل":
        return None
    for key, value in labels_dict.items():
        if value == label:
            return key
    return None


# =============================================================================
# RENDERING HELPERS
# =============================================================================

def _render_download_all_button(all_files: list, selected_source: str, file_ext: str) -> None:
    """Render download all button."""
    zip_files = []
    for file_info in all_files:
        new_info = file_info.copy()
        new_info['zip_path'] = os.path.join(
            file_info.get('source_folder', ''),
            file_info.get('target_folder', ''),
            file_info['name']
        )
        zip_files.append(new_info)
    
    zip_name = f"combined_separate_{selected_source}_{file_ext[1:]}.zip"
    zip_data = create_download_zip(zip_files, zip_name)
    st.download_button(
        label=f"📦 تحميل الملفات المعروضة ({len(all_files)})",
        data=zip_data,
        file_name=zip_name,
        mime="application/zip",
        use_container_width=True
    )
    st.markdown("---")


def _render_file_expander(file_info: dict, source: str, target: str, file_ext: str) -> None:
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
                key=f"sep_download_{source}_{target}_{file_info['name']}_{file_ext}"
            )


def _group_files_by_source_target(all_files: list) -> dict:
    """Group files by source and target branches."""
    files_grouped = {}
    for file_info in all_files:
        source = file_info.get('source_branch', 'unknown')
        target = file_info.get('target_branch', 'unknown')
        key = (source, target)
        if key not in files_grouped:
            files_grouped[key] = []
        files_grouped[key].append(file_info)
    return files_grouped


# =============================================================================
# PAGE HEADER
# =============================================================================

st.title("📂 التحويلات المنفصلة (Separate)")
st.markdown("**ملف منفصل لكل فرع مستهدف لكل فئة منتج**")
st.markdown("---")


# =============================================================================
# BRANCH SELECTION
# =============================================================================

st.subheader("📍 اختر الفرع المرسل")
st.caption("اختر فرع لعرض تحويلاته إلى كل فرع على حدة")

branches = get_branches()

# All branches button
if st.button("🌐 كل الفروع", key="sep_branch_btn_all", use_container_width=True):
    st.session_state['sep_selected_source'] = 'all'

# Branch buttons in 3 columns
column_1, column_2, column_3 = st.columns(3)
columns = [column_1, column_2, column_3, column_1, column_2, column_3]

for branch_index, branch in enumerate(branches):
    with columns[branch_index]:
        if st.button(BRANCH_LABELS.get(branch, branch), key=f"sep_branch_btn_{branch}", use_container_width=True):
            st.session_state['sep_selected_source'] = branch

# Show selected branch
if 'sep_selected_source' in st.session_state:
    selected = st.session_state['sep_selected_source']
    if selected == 'all':
        st.info("📂 عرض التحويلات المنفصلة من: **كل الفروع**")
    else:
        st.info(f"📂 عرض التحويلات المنفصلة من: **{BRANCH_LABELS.get(selected, selected)}**")
else:
    st.warning("⚠️ يرجى اختيار فرع من الأزرار أعلاه")

st.markdown("---")


# =============================================================================
# MAIN CONTENT
# =============================================================================

if 'sep_selected_source' in st.session_state:
    selected_source = st.session_state['sep_selected_source']
    
    excel_tab, csv_tab = st.tabs(["📊 ملفات Excel", "📄 ملفات CSV"])
    
    for tab, directory, file_ext in [(excel_tab, SEPARATE_EXCEL_DIR, ".xlsx"), (csv_tab, SEPARATE_CSV_DIR, ".csv")]:
        with tab:
            if not os.path.exists(directory):
                st.warning(f"المجلد غير موجود: {directory}")
                st.info("يرجى تشغيل الخطوة 11 أولاً لإنشاء ملفات التحويلات المنفصلة")
            else:
                source_folders = get_source_folders(directory, selected_source)
                
                if not source_folders:
                    st.info("لا توجد ملفات بعد. يرجى تشغيل الخطوة 11 أولاً.")
                else:
                    # Target filter
                    target_options = ["الكل"] + [BRANCH_LABELS.get(branch, branch) for branch in branches]
                    selected_target = st.selectbox("عرض التحويلات إلى:", target_options, key=f"sep_target_{file_ext}")
                    target_key = _get_key_from_label(selected_target, BRANCH_LABELS)
                    
                    # Category filter
                    category_options = ["الكل"] + list(CATEGORY_NAMES.values())
                    selected_category = st.selectbox("فلتر حسب الفئة:", category_options, key=f"sep_category_{file_ext}")
                    category_key = _get_key_from_label(selected_category, CATEGORY_NAMES)
                    
                    # Collect all files
                    all_files = []
                    for source_info in source_folders:
                        target_folders = get_target_folders(source_info['path'])
                        
                        for target_info in target_folders:
                            if target_key and target_info['target'] != target_key:
                                continue
                            
                            files = list_files_in_folder(target_info['path'], [file_ext])
                            for file_info in files:
                                file_info['source_branch'] = source_info['branch']
                                file_info['target_branch'] = target_info['target']
                                file_info['source_folder'] = source_info['name']
                                file_info['target_folder'] = target_info['name']
                            all_files.extend(files)
                    
                    # Filter by category
                    if category_key:
                        all_files = [file_info for file_info in all_files if category_key in file_info['name'].lower()]
                    
                    st.success(f"تم العثور على {len(all_files)} ملف")
                    
                    # Download and display
                    if all_files:
                        _render_download_all_button(all_files, selected_source, file_ext)
                    
                    # Group by source then target
                    files_grouped = _group_files_by_source_target(all_files)
                    
                    for (source, target), files in files_grouped.items():
                        source_name = BRANCH_LABELS.get(source, source)
                        target_name = BRANCH_LABELS.get(target, target)
                        
                        st.subheader(f"{source_name} ← {target_name}")
                        
                        for file_info in files:
                            _render_file_expander(file_info, source, target, file_ext)
                        
                        st.markdown("---")
