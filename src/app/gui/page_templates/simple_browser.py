"""Generic file browser template for surplus/shortage pages."""
import streamlit as st, os
from src.app.gui.utils.file_manager import list_output_files, organize_files_by_branch, organize_files_by_category
from src.app.gui.utils.translations import BRANCH_NAMES, CATEGORY_NAMES, MESSAGES
from src.app.gui.components import render_file_expander, render_download_all_button, get_key_from_label

def render_simple_browser(title: str, icon: str, csv_dir: str, excel_dir: str, step: int, key: str, show_branch: bool = True) -> None:
    """Render a simple file browser page."""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    from src.app.gui.utils.auth import check_password
    if not check_password(): st.stop()
    st.title(f"{icon} {title}")
    st.markdown("---")
    
    for tab, d, ext in zip(st.tabs(["📊 Excel", "📄 CSV"]), [excel_dir, csv_dir], [".xlsx", ".csv"]):
        with tab:
            if not os.path.exists(d): st.warning(f"يرجى تشغيل الخطوة {step} أولاً."); continue
            files = list_output_files(d, [ext])
            if not files: st.info(MESSAGES["no_files"]); continue
            st.success(f"تم العثور على {len(files)} ملف")
            # Filters
            by_branch, by_cat = organize_files_by_branch(files) if show_branch else {}, organize_files_by_category(files)
            filtered = files
            if show_branch and by_branch:
                sel_b = st.selectbox("الفرع:", ["الكل"] + [BRANCH_NAMES.get(b, b) for b in sorted(by_branch)], key=f"{key}_b_{ext}")
                if sel_b != "الكل": 
                    bk = get_key_from_label(sel_b, BRANCH_NAMES)
                    filtered = [f for f in filtered if bk in f['relative_path']]
            if by_cat:
                sel_c = st.selectbox("الفئة:", ["الكل"] + [CATEGORY_NAMES.get(c, c) for c in sorted(by_cat)], key=f"{key}_c_{ext}")
                if sel_c != "الكل":
                    ck = get_key_from_label(sel_c, CATEGORY_NAMES)
                    filtered = [f for f in filtered if ck in f['name'].lower()]
            # Download & display
            if filtered:
                for f in filtered: f['zip_path'] = f['relative_path']
                render_download_all_button(filtered, f"{key}_{ext[1:]}.zip")
            for f in filtered: render_file_expander(f, ext, key_prefix=key)
