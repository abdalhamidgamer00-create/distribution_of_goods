"""صفحة التحويلات المجمعة - Merged"""

import streamlit as st
import os
import sys
import pandas as pd

# Fix import path for Streamlit Cloud
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

st.set_page_config(
    page_title="التحويلات المجمعة",
    page_icon="📋",
    layout="wide"
)

# التحقق من تسجيل الدخول
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()

st.title("📋 التحويلات المجمعة (Merged)")
st.markdown("**جميع التحويلات من كل فرع في ملف واحد لكل فئة منتج**")
st.markdown("---")

# Branch selection buttons
st.subheader("📍 اختر الفرع المرسل")
st.caption("اختر فرع لعرض جميع تحويلاته المجمعة")

branches = get_branches()
branch_labels = {
    'admin': '🏢 الإدارة',
    'asherin': '🏪 العشرين',
    'wardani': '🏬 الوردانى',
    'akba': '🏭 العقبى',
    'shahid': '🏗️ الشهيد',
    'nujum': '⭐ النجوم'
}

# Create 7 buttons (All + 6 branches)
if st.button("🌐 كل الفروع", key="merged_branch_btn_all", use_container_width=True):
    st.session_state['merged_selected_branch'] = 'all'

# Remaining 6 buttons in 3 columns
col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3, col1, col2, col3]

for idx, branch in enumerate(branches):
    with cols[idx]:
        if st.button(branch_labels.get(branch, branch), key=f"merged_branch_btn_{branch}", use_container_width=True):
            st.session_state['merged_selected_branch'] = branch

# Show selected branch
if 'merged_selected_branch' in st.session_state:
    selected = st.session_state['merged_selected_branch']
    if selected == 'all':
        st.info("📂 عرض التحويلات المجمعة من: **كل الفروع**")
    else:
        st.info(f"📂 عرض التحويلات المجمعة من: **{branch_labels.get(selected, selected)}**")
else:
    st.warning("⚠️ يرجى اختيار فرع من الأزرار أعلاه")

st.markdown("---")

# مجلدات المخرجات
merged_csv_dir = os.path.join("data", "output", "combined_transfers", "merged", "csv")
merged_excel_dir = os.path.join("data", "output", "combined_transfers", "merged", "excel")


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


def _build_file_info(folder_path: str, filename: str) -> dict:
    """Build file info dict."""
    filepath = os.path.join(folder_path, filename)
    return {'name': filename, 'path': filepath, 'size': os.path.getsize(filepath), 'relative_path': filename}


def list_files_in_folder(folder_path, extensions):
    """List files in a folder."""
    if not os.path.exists(folder_path):
        return []
    return [_build_file_info(folder_path, f) for f in os.listdir(folder_path) if any(f.endswith(e) for e in extensions)]


# Only show files if a branch is selected
if 'merged_selected_branch' in st.session_state:
    selected_branch = st.session_state['merged_selected_branch']
    
    # تبويبات للـ CSV و Excel
    tab1, tab2 = st.tabs(["📊 ملفات Excel", "📄 ملفات CSV"])
    
    for tab, directory, file_ext in [(tab1, merged_excel_dir, ".xlsx"), (tab2, merged_csv_dir, ".csv")]:
        with tab:
            if not os.path.exists(directory):
                st.warning(f"المجلد غير موجود: {directory}")
                st.info("يرجى تشغيل الخطوة 11 أولاً لإنشاء ملفات التحويلات المجمعة")
            else:
                branch_folders = get_branch_folders(directory, selected_branch)
                
                if not branch_folders:
                    st.info("لا توجد ملفات بعد. يرجى تشغيل الخطوة 11 أولاً.")
                else:
                    # فلتر حسب الفئة
                    category_options = ["الكل"] + list(CATEGORY_NAMES.values())
                    selected_category = st.selectbox(
                        "فلتر حسب الفئة:",
                        category_options,
                        key=f"merged_category_{file_ext}"
                    )
                    
                    # Get category key
                    category_key = None
                    if selected_category != "الكل":
                        for k, v in CATEGORY_NAMES.items():
                            if v == selected_category:
                                category_key = k
                                break
                    
                    # Collect all files from selected folders
                    all_files = []
                    for folder_info in branch_folders:
                        files = list_files_in_folder(folder_info['path'], [file_ext])
                        for f in files:
                            f['branch'] = folder_info['branch']
                            f['folder_name'] = folder_info['name']
                        all_files.extend(files)
                    
                    # Filter by category
                    if category_key:
                        all_files = [f for f in all_files if category_key in f['name'].lower()]
                    
                    st.success(f"تم العثور على {len(all_files)} ملف")
                    
                    # زر تحميل الكل
                    if all_files:
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
                    
                    # Group by branch for display
                    files_by_branch = {}
                    for f in all_files:
                        branch = f.get('branch', 'unknown')
                        if branch not in files_by_branch:
                            files_by_branch[branch] = []
                        files_by_branch[branch].append(f)
                    
                    # عرض كل فرع
                    for branch, files in files_by_branch.items():
                        branch_name = branch_labels.get(branch, branch)
                        st.subheader(f"{branch_name}")
                        
                        for file_info in files:
                            with st.expander(f"📄 {file_info['name']} ({get_file_size_str(file_info['size'])})"):
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    df = read_file_for_display(file_info['path'], max_rows=50)
                                    if df is not None:
                                        st.dataframe(df, use_container_width=True)
                                        st.caption(f"عرض أول 50 صف")
                                
                                with col2:
                                    with open(file_info['path'], 'rb') as f:
                                        file_data = f.read()
                                    
                                    st.download_button(
                                        label="⬇️ تحميل",
                                        data=file_data,
                                        file_name=file_info['name'],
                                        mime="application/octet-stream",
                                        key=f"merged_download_{file_info['name']}_{file_ext}"
                                    )
                        
                        st.markdown("---")
