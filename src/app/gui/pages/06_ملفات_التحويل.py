"""صفحة ملفات التحويل"""

import streamlit as st
import os
import sys
import re

# Path configuration
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app.gui.utils.file_manager import list_output_files
from src.app.gui.components import (
    BRANCH_LABELS, render_branch_selection_buttons, render_selected_branch_info,
    render_file_expander, render_download_all_button, get_branch_key_from_label
)
from src.core.domain.branches.config import get_branches

# Page config
st.set_page_config(page_title="ملفات التحويل", page_icon="📤", layout="wide")

# Auth
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()

# Constants
CSV_DIR = os.path.join("data", "output", "transfers", "csv")
EXCEL_DIR = os.path.join("data", "output", "transfers", "excel")
SESSION_KEY = 'selected_source_branch'


def get_branch_folder(branch: str, file_ext: str) -> str:
    """Get folder name for branch."""
    prefix = "transfers_from_" if file_ext == ".csv" else "transfers_excel_from_"
    return f"{prefix}{branch}_to_other_branches"


def collect_files(directory: str, branches: list, selected: str, file_ext: str) -> list:
    """Collect files for selected branch(es)."""
    all_files = []
    target_branches = branches if selected == 'all' else [selected]
    for branch in target_branches:
        path = os.path.join(directory, get_branch_folder(branch, file_ext))
        if os.path.exists(path):
            all_files.extend(list_output_files(path, [file_ext]))
    return all_files


def prepare_zip(files: list) -> list:
    """Prepare files with zip paths."""
    for f in files:
        match = re.search(r'(from_\w+_to_\w+)', f.get('relative_path', '') + f['name'])
        f['zip_path'] = os.path.join(match.group(1) if match else 'other', f['name'])
    return files


# Header
st.title("📤 ملفات التحويل")
st.markdown("---")

# Branch selection
st.subheader("📍 اختر الفرع المصدر")
render_branch_selection_buttons(SESSION_KEY, "transfers")
selected = render_selected_branch_info(SESSION_KEY, "📂 عرض التحويلات من: **{branch_name}** → الفروع الأخرى")
st.markdown("---")

# Main content
if selected:
    branches = get_branches()
    excel_tab, csv_tab = st.tabs(["📊 ملفات Excel", "📄 ملفات CSV"])
    
    for tab, directory, ext in [(excel_tab, EXCEL_DIR, ".xlsx"), (csv_tab, CSV_DIR, ".csv")]:
        with tab:
            if not os.path.exists(directory):
                st.warning("المجلد غير موجود. يرجى تشغيل الخطوة 7 أولاً.")
                continue
            
            files = collect_files(directory, branches, selected, ext)
            if not files:
                st.warning(f"لا توجد تحويلات من {BRANCH_LABELS.get(selected, selected)}")
                continue
            
            # Target filter
            opts = ["الكل"] + [BRANCH_LABELS.get(b, b) for b in branches if selected == 'all' or b != selected]
            target = st.selectbox("عرض التحويلات إلى:", opts, key=f"target_{ext}")
            target_key = get_branch_key_from_label(target)
            
            filtered = [f for f in files if not target_key or f"to_{target_key}" in f['relative_path'] + f['name']]
            st.success(f"تم العثور على {len(filtered)} ملف")
            
            if filtered:
                zip_name = f"transfers_{selected}_to_{target_key or 'all'}_{ext[1:]}.zip"
                render_download_all_button(prepare_zip(filtered), zip_name)
            
            for f in filtered:
                render_file_expander(f, ext, key_prefix="transfers")
