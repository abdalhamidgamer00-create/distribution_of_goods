"""صفحة الفائض المتبقي"""

import streamlit as st
import os
import sys

# Path configuration
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app.gui.utils.file_manager import list_output_files, organize_files_by_branch, organize_files_by_category
from src.app.gui.utils.translations import BRANCH_NAMES, CATEGORY_NAMES, MESSAGES
from src.app.gui.components import render_file_expander, render_download_all_button, get_key_from_label

# Page config
st.set_page_config(page_title="الفائض المتبقي", page_icon="📦", layout="wide")

# Auth
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()

# Constants
CSV_DIR = os.path.join("data", "output", "remaining_surplus", "csv")
EXCEL_DIR = os.path.join("data", "output", "remaining_surplus", "excel")

# Header
st.title("📦 الفائض المتبقي")
st.markdown("---")

# Main content
excel_tab, csv_tab = st.tabs(["📊 ملفات Excel", "📄 ملفات CSV"])

for tab, directory, ext in [(excel_tab, EXCEL_DIR, ".xlsx"), (csv_tab, CSV_DIR, ".csv")]:
    with tab:
        if not os.path.exists(directory):
            st.warning("المجلد غير موجود. يرجى تشغيل الخطوة 9 أولاً.")
            continue
        
        files = list_output_files(directory, [ext])
        if not files:
            st.info(MESSAGES["no_files"])
            continue
        
        st.success(f"تم العثور على {len(files)} ملف")
        
        # Filters
        by_branch = organize_files_by_branch(files)
        by_category = organize_files_by_category(files)
        
        branch_opts = ["الكل"] + [BRANCH_NAMES.get(b, b) for b in sorted(by_branch.keys())]
        cat_opts = ["الكل"] + [CATEGORY_NAMES.get(c, c) for c in sorted(by_category.keys())]
        
        sel_branch = st.selectbox("اختر الفرع:", branch_opts, key=f"branch_{ext}")
        sel_cat = st.selectbox("اختر الفئة:", cat_opts, key=f"cat_{ext}")
        
        # Filter files
        filtered = files
        if sel_branch != "الكل":
            branch_key = get_key_from_label(sel_branch, BRANCH_NAMES)
            filtered = [f for f in filtered if branch_key in f['relative_path']]
        if sel_cat != "الكل":
            cat_key = get_key_from_label(sel_cat, CATEGORY_NAMES)
            filtered = [f for f in filtered if cat_key in f['name'].lower()]
        
        # Download all
        if filtered:
            for f in filtered:
                f['zip_path'] = f['relative_path']
            render_download_all_button(filtered, f"remaining_surplus_{ext[1:]}.zip")
        
        # Display files
        for f in filtered:
            render_file_expander(f, ext, key_prefix="surplus")
