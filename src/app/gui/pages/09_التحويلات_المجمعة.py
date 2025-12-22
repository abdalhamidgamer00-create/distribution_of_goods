"""صفحة التحويلات المجمعة - Merged"""

import streamlit as st
import os
import sys

# Path configuration
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app.gui.utils.translations import CATEGORY_NAMES
from src.app.gui.components import (
    BRANCH_LABELS, render_branch_selection_buttons, render_selected_branch_info,
    render_download_all_button, get_key_from_label, group_files_by_branch, render_file_expander
)
from src.app.gui.page_templates import list_files_in_folder, get_matching_folders

# Page config
st.set_page_config(page_title="التحويلات المجمعة", page_icon="📋", layout="wide")

# Auth
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()

# Constants
MERGED_CSV = os.path.join("data", "output", "combined_transfers", "merged", "csv")
MERGED_EXCEL = os.path.join("data", "output", "combined_transfers", "merged", "excel")
SESSION_KEY = 'merged_selected_branch'

# Header
st.title("📋 التحويلات المجمعة (Merged)")
st.markdown("**جميع التحويلات من كل فرع في ملف واحد لكل فئة منتج**")
st.markdown("---")

# Branch selection
st.subheader("📍 اختر الفرع المرسل")
render_branch_selection_buttons(SESSION_KEY, "merged")
selected_branch = render_selected_branch_info(SESSION_KEY, "📂 عرض التحويلات المجمعة من: **{branch_name}**")
st.markdown("---")

# Main content
if selected_branch:
    excel_tab, csv_tab = st.tabs(["📊 ملفات Excel", "📄 ملفات CSV"])
    
    for tab, directory, file_ext in [(excel_tab, MERGED_EXCEL, ".xlsx"), (csv_tab, MERGED_CSV, ".csv")]:
        with tab:
            if not os.path.exists(directory):
                st.warning(f"المجلد غير موجود. يرجى تشغيل الخطوة 11 أولاً.")
                continue
            
            folders = get_matching_folders(directory, 'combined_transfers_from_', selected_branch)
            if not folders:
                st.info("لا توجد ملفات بعد.")
                continue
            
            # Category filter
            category = st.selectbox("فلتر حسب الفئة:", ["الكل"] + list(CATEGORY_NAMES.values()), key=f"merged_cat_{file_ext}")
            category_key = get_key_from_label(category, CATEGORY_NAMES)
            
            # Collect files
            all_files = []
            for folder in folders:
                files = list_files_in_folder(folder['path'], [file_ext])
                for f in files:
                    f['branch'] = folder['branch']
                    f['folder_name'] = folder['name']
                all_files.extend(files)
            
            if category_key:
                all_files = [f for f in all_files if category_key in f['name'].lower()]
            
            st.success(f"تم العثور على {len(all_files)} ملف")
            
            # Download
            if all_files:
                zip_files = [{**f, 'zip_path': os.path.join(f.get('folder_name', ''), f['name'])} for f in all_files]
                render_download_all_button(zip_files, f"merged_{selected_branch}_{file_ext[1:]}.zip")
            
            # Display grouped
            for branch, files in group_files_by_branch(all_files).items():
                st.subheader(BRANCH_LABELS.get(branch, branch))
                for f in files:
                    render_file_expander(f, file_ext, key_prefix="merged")
                st.markdown("---")
