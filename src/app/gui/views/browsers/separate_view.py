"""Separate transfers browser view."""
import os
import streamlit as st
from src.core.domain.branches.config import get_branches
from src.app.gui.utils.translations import CATEGORY_NAMES
from src.app.gui.services.file_service import (
    group_files_by_source_target,
    list_files_in_folder,
    get_matching_folders,
    collect_separate_files
)
from src.app.gui.components import (
    BRANCH_LABELS,
    render_file_expander,
    render_download_all_button,
    render_branch_selection_section,
    setup_browser_page,
    render_browser_tabs,
    get_key_from_label,
    get_branch_key_from_label
)
from src.app.gui.services.file_service import (
    group_files_by_source_target,
    list_files_in_folder,
    get_matching_folders
)


# =============================================================================
# PUBLIC API
# =============================================================================

def render_separate_browser(
    title: str,
    icon: str,
    csv: str,
    excel: str,
    step: int,
    sk: str,
    kp: str
) -> None:
    """Render separate transfers browser."""
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
        lambda d, e: _process_separate_tab(d, e, step, kp, selected_branch)
    )


# =============================================================================
# PRIVATE HELPERS: SEPARATE LOGIC
# =============================================================================




def _process_separate_tab(
    directory: str,
    ext: str,
    step: int,
    kp: str,
    sel: str
) -> None:
    """Process single tab logic for separate transfers."""
    if not os.path.exists(directory):
        st.warning(f"يرجى تشغيل الخطوة {step} أولاً.")
        return

    sources = get_matching_folders(directory, 'transfers_from_', sel)
    
    if not sources:
        st.info("لا توجد ملفات")
        return

    tk, ck = _render_filters(kp, ext)
    files = collect_separate_files(sources, ext, tk, ck)
    
    st.success(f"تم العثور على {len(files)} ملف")
    
    if files:
        _display_separate(files, kp, sel, ext)


def _render_filters(kp: str, ext: str) -> tuple:
    """Render filters for separate files and return keys."""
    branches = get_branches()
    
    tgl_opts = ["الكل"] + [BRANCH_LABELS.get(b, b) for b in branches]
    tl = st.selectbox("إلى:", tgl_opts, key=f"{kp}_t_{ext}")
    
    cat_opts = ["الكل"] + list(CATEGORY_NAMES.values())
    cl = st.selectbox("الفئة:", cat_opts, key=f"{kp}_c_{ext}")
    
    tk = get_key_from_label(tl, BRANCH_LABELS)
    ck = get_key_from_label(cl, CATEGORY_NAMES)
    
    return tk, ck


def _display_separate(
    files: list,
    kp: str,
    sel: str,
    ext: str
) -> None:
    """Display separate files grouped by source/target."""
    for f in files:
        f['zip_path'] = os.path.join(
            f['source_folder'], 
            f['target_folder'], 
            f['name']
        )
        
    render_download_all_button(files, f"{kp}_{sel}_{ext[1:]}.zip")
    
    grouped = group_files_by_source_target(files)
    for (s, t), fs in grouped.items():
        header = f"{BRANCH_LABELS.get(s, s)} ← {BRANCH_LABELS.get(t, t)}"
        st.subheader(header)
        
        for f in fs:
            render_file_expander(
                f, ext, key_prefix=f"{kp}_{s}_{t}"
            )
        st.markdown("---")
