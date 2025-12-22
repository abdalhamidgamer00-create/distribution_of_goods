"""صفحة التحويلات المنفصلة - Separate"""

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
    render_download_all_button, get_key_from_label, group_files_by_source_target, render_file_expander
)
from src.app.gui.page_templates import list_files_in_folder, get_matching_folders
from src.core.domain.branches.config import get_branches

# Page config
st.set_page_config(page_title="التحويلات المنفصلة", page_icon="📂", layout="wide")

# Auth
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()

# Constants
CSV_DIR, EXCEL_DIR = os.path.join("data", "output", "combined_transfers", "separate", "csv"), os.path.join("data", "output", "combined_transfers", "separate", "excel")
SESSION_KEY = 'sep_selected_source'


def get_target_folders(source_path: str) -> list:
    """Get target folders within source folder."""
    if not os.path.exists(source_path):
        return []
    return [{'name': n, 'path': os.path.join(source_path, n), 'target': n.replace('to_', '')}
            for n in os.listdir(source_path) if os.path.isdir(os.path.join(source_path, n)) and n.startswith('to_')]


# Header
st.title("📂 التحويلات المنفصلة (Separate)")
st.markdown("**ملف منفصل لكل فرع مستهدف لكل فئة منتج**")
st.markdown("---")

# Branch selection
st.subheader("📍 اختر الفرع المرسل")
render_branch_selection_buttons(SESSION_KEY, "sep")
selected = render_selected_branch_info(SESSION_KEY, "📂 عرض التحويلات المنفصلة من: **{branch_name}**")
st.markdown("---")

# Main content
if selected:
    branches = get_branches()
    excel_tab, csv_tab = st.tabs(["📊 ملفات Excel", "📄 ملفات CSV"])
    
    for tab, directory, ext in [(excel_tab, EXCEL_DIR, ".xlsx"), (csv_tab, CSV_DIR, ".csv")]:
        with tab:
            if not os.path.exists(directory):
                st.warning("المجلد غير موجود. يرجى تشغيل الخطوة 11 أولاً.")
                continue
            
            sources = get_matching_folders(directory, 'transfers_from_', selected)
            if not sources:
                st.info("لا توجد ملفات بعد.")
                continue
            
            # Filters
            target_label = st.selectbox("عرض التحويلات إلى:", ["الكل"] + [BRANCH_LABELS.get(b, b) for b in branches], key=f"sep_t_{ext}")
            cat_label = st.selectbox("فلتر حسب الفئة:", ["الكل"] + list(CATEGORY_NAMES.values()), key=f"sep_c_{ext}")
            target_key, cat_key = get_key_from_label(target_label, BRANCH_LABELS), get_key_from_label(cat_label, CATEGORY_NAMES)
            
            # Collect files
            all_files = []
            for src in sources:
                for tgt in get_target_folders(src['path']):
                    if target_key and tgt['target'] != target_key:
                        continue
                    for f in list_files_in_folder(tgt['path'], [ext]):
                        f.update({'source_branch': src['branch'], 'target_branch': tgt['target'],
                                  'source_folder': src['name'], 'target_folder': tgt['name']})
                        all_files.append(f)
            
            if cat_key:
                all_files = [f for f in all_files if cat_key in f['name'].lower()]
            
            st.success(f"تم العثور على {len(all_files)} ملف")
            
            # Download
            if all_files:
                for f in all_files:
                    f['zip_path'] = os.path.join(f['source_folder'], f['target_folder'], f['name'])
                render_download_all_button(all_files, f"separate_{selected}_{ext[1:]}.zip")
            
            # Display grouped
            for (src, tgt), files in group_files_by_source_target(all_files).items():
                st.subheader(f"{BRANCH_LABELS.get(src, src)} ← {BRANCH_LABELS.get(tgt, tgt)}")
                for f in files:
                    render_file_expander(f, ext, key_prefix=f"sep_{src}_{tgt}")
                st.markdown("---")
