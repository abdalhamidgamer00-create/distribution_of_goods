"""صفحة النقص"""

import streamlit as st
import os
import sys

# Path configuration
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app.gui.utils.file_manager import list_output_files, organize_files_by_category, read_file_for_display, get_file_size_str
from src.app.gui.utils.translations import CATEGORY_NAMES, MESSAGES
from src.app.gui.components import render_download_all_button, get_key_from_label

# Page config
st.set_page_config(page_title="النقص", page_icon="⚠️", layout="wide")

# Auth
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()

# Constants
CSV_DIR = os.path.join("data", "output", "shortage", "csv")
EXCEL_DIR = os.path.join("data", "output", "shortage", "excel")


def render_shortage_expander(file_info: dict, ext: str) -> None:
    """Render file expander with shortage-specific metrics."""
    with st.expander(f"📄 {file_info['name']} ({get_file_size_str(file_info['size'])})"):
        col1, col2 = st.columns([3, 1])
        with col1:
            df = read_file_for_display(file_info['path'], max_rows=100)
            if df is not None:
                st.dataframe(df, use_container_width=True)
                if 'shortage_quantity' in df.columns:
                    st.metric("إجمالي النقص", f"{int(df['shortage_quantity'].sum()):,} وحدة")
                st.caption("عرض أول 100 صف")
        with col2:
            with open(file_info['path'], 'rb') as f:
                st.download_button("⬇️ تحميل", f.read(), file_info['name'], "application/octet-stream", key=f"dl_{file_info['name']}_{ext}")


# Header
st.title("⚠️ النقص في المنتجات")
st.markdown("---")

# Main content
excel_tab, csv_tab = st.tabs(["📊 ملفات Excel", "📄 ملفات CSV"])

for tab, directory, ext in [(excel_tab, EXCEL_DIR, ".xlsx"), (csv_tab, CSV_DIR, ".csv")]:
    with tab:
        if not os.path.exists(directory):
            st.warning("المجلد غير موجود. يرجى تشغيل الخطوة 10 أولاً.")
            continue
        
        files = list_output_files(directory, [ext])
        if not files:
            st.info(MESSAGES["no_files"])
            continue
        
        st.success(f"تم العثور على {len(files)} ملف")
        
        # Category filter
        by_cat = organize_files_by_category(files)
        cat_opts = ["الكل"] + [CATEGORY_NAMES.get(c, c) for c in sorted(by_cat.keys())]
        sel_cat = st.selectbox("اختر الفئة:", cat_opts, key=f"cat_{ext}")
        
        # Filter
        filtered = files
        if sel_cat != "الكل":
            cat_key = get_key_from_label(sel_cat, CATEGORY_NAMES)
            filtered = [f for f in files if cat_key in f['name'].lower()]
        
        # Download all
        if filtered:
            render_download_all_button(filtered, f"shortage_{ext[1:]}.zip")
        
        # Display files
        for f in filtered:
            render_shortage_expander(f, ext)
