"""صفحة الفائض المتبقي"""

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
    get_file_size_str,
    organize_files_by_branch,
    organize_files_by_category
)
from src.app.gui.utils.translations import BRANCH_NAMES, CATEGORY_NAMES, MESSAGES


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="الفائض المتبقي",
    page_icon="📦",
    layout="wide"
)


# =============================================================================
# AUTHENTICATION
# =============================================================================

from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()


# =============================================================================
# PAGE HEADER
# =============================================================================

st.title("📦 الفائض المتبقي")
st.markdown("---")


# =============================================================================
# CONSTANTS
# =============================================================================

SURPLUS_CSV_DIR = os.path.join("data", "output", "remaining_surplus", "csv")
SURPLUS_EXCEL_DIR = os.path.join("data", "output", "remaining_surplus", "excel")


# =============================================================================
# FILE DISPLAY HELPERS
# =============================================================================

def _get_branch_key(selected_branch: str) -> str:
    """Get branch key from translated name."""
    for key, name in BRANCH_NAMES.items():
        if name == selected_branch:
            return key
    return None


def _get_category_key(selected_category: str) -> str:
    """Get category key from translated name."""
    for key, name in CATEGORY_NAMES.items():
        if name == selected_category:
            return key
    return None


def _filter_files(files: list, selected_branch: str, selected_category: str) -> list:
    """Filter files based on selected branch and category."""
    display_files = files
    
    if selected_branch != "الكل":
        branch_key = _get_branch_key(selected_branch)
        display_files = [file_info for file_info in display_files if branch_key in file_info['relative_path']]
    
    if selected_category != "الكل":
        category_key = _get_category_key(selected_category)
        display_files = [file_info for file_info in display_files if category_key in file_info['name'].lower()]
    
    return display_files


def _render_download_all_button(display_files: list, file_ext: str) -> None:
    """Render download all button."""
    zip_files = []
    for file_info in display_files:
        new_info = file_info.copy()
        new_info['zip_path'] = file_info['relative_path']
        zip_files.append(new_info)
        
    zip_data = create_download_zip(zip_files, f"remaining_surplus_{file_ext[1:]}.zip")
    st.download_button(
        label=f"📦 تحميل جميع ملفات {file_ext[1:].upper()}",
        data=zip_data,
        file_name=f"remaining_surplus_{file_ext[1:]}.zip",
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
                key=f"download_{file_info['name']}_{file_ext}"
            )


# =============================================================================
# MAIN CONTENT
# =============================================================================

excel_tab, csv_tab = st.tabs(["📊 ملفات Excel", "📄 ملفات CSV"])

for tab, directory, file_ext in [(excel_tab, SURPLUS_EXCEL_DIR, ".xlsx"), (csv_tab, SURPLUS_CSV_DIR, ".csv")]:
    with tab:
        if not os.path.exists(directory):
            st.warning(f"المجلد غير موجود: {directory}")
            st.info("يرجى تشغيل الخطوة 10 أولاً لإنشاء ملفات الفائض المتبقي")
        else:
            files = list_output_files(directory, [file_ext])
            
            if not files:
                st.info(MESSAGES["no_files"])
            else:
                st.success(f"تم العثور على {len(files)} ملف")
                
                by_branch = organize_files_by_branch(files)
                by_category = organize_files_by_category(files)
                
                branch_options = ["الكل"] + [BRANCH_NAMES.get(branch, branch) for branch in sorted(by_branch.keys())]
                selected_branch = st.selectbox("اختر الفرع:", branch_options, key=f"branch_{file_ext}")
                
                category_options = ["الكل"] + [CATEGORY_NAMES.get(category, category) for category in sorted(by_category.keys())]
                selected_category = st.selectbox("اختر الفئة:", category_options, key=f"category_{file_ext}")
                
                display_files = _filter_files(files, selected_branch, selected_category)
                
                if display_files:
                    _render_download_all_button(display_files, file_ext)
                
                for file_info in display_files:
                    _render_file_expander(file_info, file_ext)
