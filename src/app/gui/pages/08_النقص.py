"""صفحة النقص"""

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
    organize_files_by_category
)
from src.app.gui.utils.translations import CATEGORY_NAMES, MESSAGES


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="النقص",
    page_icon="⚠️",
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

st.title("⚠️ النقص في المنتجات")
st.markdown("---")


# =============================================================================
# CONSTANTS
# =============================================================================

SHORTAGE_CSV_DIR = os.path.join("data", "output", "shortage", "csv")
SHORTAGE_EXCEL_DIR = os.path.join("data", "output", "shortage", "excel")


# =============================================================================
# FILE FILTERING HELPERS
# =============================================================================

def _get_category_key(selected_category: str) -> str:
    """Get category key from translated name."""
    for key, name in CATEGORY_NAMES.items():
        if name == selected_category:
            return key
    return None


def _filter_files_by_category(files: list, selected_category: str, file_ext: str) -> list:
    """Filter files based on selected category."""
    if selected_category == "الكل":
        return files
    
    category_key = _get_category_key(selected_category)
    return [file_info for file_info in files 
            if category_key in file_info['name'].lower() or file_info['name'].endswith(f"_{category_key}{file_ext}")]


# =============================================================================
# RENDERING HELPERS
# =============================================================================

def _render_download_all_button(display_files: list, file_ext: str) -> None:
    """Render download all button."""
    zip_data = create_download_zip(display_files, f"shortage_{file_ext[1:]}.zip")
    st.download_button(
        label=f"📦 تحميل جميع ملفات {file_ext[1:].upper()}",
        data=zip_data,
        file_name=f"shortage_{file_ext[1:]}.zip",
        mime="application/zip",
        use_container_width=True
    )
    st.markdown("---")


def _render_file_expander(file_info: dict, file_ext: str) -> None:
    """Render file expander with dataframe and download button."""
    with st.expander(f"📄 {file_info['name']} ({get_file_size_str(file_info['size'])})"):
        content_column, download_column = st.columns([3, 1])
        
        with content_column:
            dataframe = read_file_for_display(file_info['path'], max_rows=100)
            if dataframe is not None:
                st.dataframe(dataframe, use_container_width=True)
                
                if 'shortage_quantity' in dataframe.columns:
                    total_shortage = dataframe['shortage_quantity'].sum()
                    st.metric("إجمالي النقص", f"{int(total_shortage):,} وحدة")
                
                st.caption("عرض أول 100 صف")
        
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

for tab, directory, file_ext in [(excel_tab, SHORTAGE_EXCEL_DIR, ".xlsx"), (csv_tab, SHORTAGE_CSV_DIR, ".csv")]:
    with tab:
        if not os.path.exists(directory):
            st.warning(f"المجلد غير موجود: {directory}")
            st.info("يرجى تشغيل الخطوة 11 أولاً لإنشاء ملفات النقص")
        else:
            files = list_output_files(directory, [file_ext])
            
            if not files:
                st.info(MESSAGES["no_files"])
            else:
                st.success(f"تم العثور على {len(files)} ملف")
                
                by_category = organize_files_by_category(files)
                
                category_options = ["الكل"] + [CATEGORY_NAMES.get(category, category) for category in sorted(by_category.keys())]
                selected_category = st.selectbox("اختر الفئة:", category_options, key=f"category_{file_ext}")
                
                display_files = _filter_files_by_category(files, selected_category, file_ext)
                
                if display_files:
                    _render_download_all_button(display_files, file_ext)
                
                for file_info in display_files:
                    _render_file_expander(file_info, file_ext)
