"""Transfers file browser view."""
import os
import re
import streamlit as st
from src.core.domain.branches.config import get_branches
from src.app.gui.services.file_service import (
    list_output_files,
    collect_transfer_files
)
from src.app.gui.components import (
    BRANCH_LABELS,
    render_branch_selection_section,
    render_file_expander,
    render_download_all_button,
    get_branch_key_from_label,
    setup_browser_page,
    render_browser_tabs
)


# =============================================================================
# PUBLIC API
# =============================================================================

def render_transfers_browser(
    title: str,
    icon: str,
    csv: str,
    excel: str,
    step: int,
    sk: str,
    kp: str
) -> None:
    """Render transfer files browser with branch selection."""
    if not setup_browser_page(title, icon):
        return
    
    selected_branch = render_branch_selection_section(
        session_key=sk,
        subheader_label="📍 اختر الفرع المصدر",
        info_message_template="📂 عرض من: **{branch_name}**"
    )

    if not selected_branch:
        return

    branches = get_branches()
    render_browser_tabs(
        csv, 
        excel,
        lambda d, e: _process_transfer_tab(d, e, step, kp, selected_branch, branches)
    )


def _process_transfer_tab(
    directory: str,
    ext: str,
    step: int,
    kp: str,
    sel: str,
    branches: list
) -> None:
    """Process single tab logic for transfers."""
    if not os.path.exists(directory):
        st.warning(f"يرجى تشغيل الخطوة {step} أولاً.")
        return

    files = collect_transfer_files(directory, ext, sel, branches)
    
    if not files:
        st.warning("لا توجد ملفات")
        return

    files = _filter_transfers(files, sel, branches, kp, ext)
    
    if files:
        _display_transfers(files, kp, sel, ext)


def _filter_transfers(
    files: list,
    sel: str,
    branches: list,
    kp: str,
    ext: str
) -> list:
    """Filter transfer files by target branch."""
    opts = ["الكل"] + [
        BRANCH_LABELS.get(b, b) 
        for b in branches 
        if sel == 'all' or b != sel
    ]
    
    tgt = st.selectbox("إلى:", opts, key=f"{kp}_t_{ext}")
    tk = get_branch_key_from_label(tgt)
    
    if not tk:
        return files
        
    return [
        f for f in files 
        if f"to_{tk}" in f['relative_path'] + f['name']
    ]


def _display_transfers(
    files: list,
    kp: str,
    sel: str,
    ext: str
) -> None:
    """Display collected transfer files."""
    st.success(f"تم العثور على {len(files)} ملف")
    
    for f in files:
        m = re.search(
            r'(from_\w+_to_\w+)', 
            f.get('relative_path', '') + f['name']
        )
        f['zip_path'] = os.path.join(
            m.group(1) if m else 'other', 
            f['name']
        )
        
    zip_name = f"{kp}_{sel}_{ext[1:]}.zip"
    render_download_all_button(files, zip_name)
    
    for f in files:
        render_file_expander(f, ext, key_prefix=kp)
