"""Merged transfers browser view."""
import os
import streamlit as st
from src.app.gui.utils.translations import CATEGORY_NAMES
from src.app.gui.components import (
    BRANCH_LABELS,
    render_branch_selection_section,
    render_selected_branch_info,
    render_file_expander,
    render_download_all_button,
    get_key_from_label,
    setup_browser_page,
    render_browser_tabs
)
from src.app.gui.services.file_service import (
    group_files_by_branch,
    list_files_in_folder,
    get_matching_folders
)


# =============================================================================
# PUBLIC API
# =============================================================================

def render_merged_browser(
    title: str,
    icon: str,
    csv: str,
    excel: str,
    step: int,
    sk: str,
    kp: str
) -> None:
    """Render merged transfers browser."""
    if not setup_browser_page(title, icon):
        return

    selected_branch = render_branch_selection_section(
        session_key=sk,
        subheader_label="📍 اختر الفرع المرسل",
        info_message_template="📂 من: **{branch_name}**"
    )
    
    if not selected_branch:
        return

    render_browser_tabs(
        csv, 
        excel, 
        lambda d, e: _process_merged_tab(d, e, step, kp, selected_branch)
    )


def _process_merged_tab(
    directory: str,
    ext: str,
    step: int,
    kp: str,
    sel: str
) -> None:
    """Process single tab logic for merged transfers."""
    if not os.path.exists(directory):
        st.warning(f"يرجى تشغيل الخطوة {step} أولاً.")
        return

    folders = get_matching_folders(
        directory, 'combined_transfers_from_', sel
    )
    
    if not folders:
        st.info("لا توجد ملفات")
        return

    files = _collect_merged_files(folders, ext)
    files = _filter_merged_by_cat(files, kp, ext)
    
    st.success(f"تم العثور على {len(files)} ملف")
    
    if files:
        _display_merged(files, kp, sel, ext)


def _collect_merged_files(folders: list, ext: str) -> list:
    """Collect all files from matching folders."""
    files = []
    for fo in folders:
        for f in list_files_in_folder(fo['path'], [ext]):
            f['branch'] = fo['branch']
            f['folder_name'] = fo['name']
            files.append(f)
    return files


def _filter_merged_by_cat(files: list, kp: str, ext: str) -> list:
    """Filter merged files by category."""
    cat_opts = ["الكل"] + list(CATEGORY_NAMES.values())
    cat = st.selectbox("الفئة:", cat_opts, key=f"{kp}_c_{ext}")
    ck = get_key_from_label(cat, CATEGORY_NAMES)
    
    if not ck:
        return files
        
    return [f for f in files if ck in f['name'].lower()]


def _display_merged(
    files: list,
    kp: str,
    sel: str,
    ext: str
) -> None:
    """Display merged files grouped by branch."""
    for f in files:
        f['zip_path'] = os.path.join(
            f.get('folder_name', ''), 
            f['name']
        )
        
    render_download_all_button(files, f"{kp}_{sel}_{ext[1:]}.zip")
    
    grouped = group_files_by_branch(files)
    for b, fs in grouped.items():
        st.subheader(BRANCH_LABELS.get(b, b))
        for f in fs:
            render_file_expander(f, ext, key_prefix=kp)
        st.markdown("---")
