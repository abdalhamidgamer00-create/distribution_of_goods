"""Generic branch-based file browser template."""
import streamlit as st
import os
import re
from src.app.gui.utils.file_manager import list_output_files
from src.app.gui.utils.translations import CATEGORY_NAMES
from src.app.gui.components import (
    BRANCH_LABELS,
    render_branch_selection_buttons,
    render_selected_branch_info,
    render_file_expander,
    render_download_all_button,
    get_key_from_label,
    get_branch_key_from_label,
    group_files_by_branch,
    group_files_by_source_target
)
from src.app.gui.page_templates import (
    list_files_in_folder,
    get_matching_folders
)
from src.core.domain.branches.config import get_branches


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
    _setup_page(title, icon)
    
    selected_branch = _handle_branch_selection(sk)
    if not selected_branch:
        return

    _render_transfer_tabs(
        csv, excel, step, kp, selected_branch
    )


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
    _setup_page(title, icon)

    selected_branch = _handle_branch_selection(sk, source_label=True)
    if not selected_branch:
        return

    _render_merged_tabs(
        csv, excel, step, kp, selected_branch
    )


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
    _setup_page(title, icon)

    selected_branch = _handle_branch_selection(sk, source_label=True)
    if not selected_branch:
        return

    _render_separate_tabs(
        csv, excel, step, kp, selected_branch
    )


# =============================================================================
# PRIVATE HELPERS: SETUP & UI
# =============================================================================

def _setup_page(title: str, icon: str) -> None:
    """Initialize page, check auth, and render header."""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    
    from src.app.gui.utils.auth import check_password
    if not check_password():
        st.stop()
        
    st.title(f"{icon} {title}")
    st.markdown("---")


def _handle_branch_selection(
    session_key: str,
    source_label: bool = False
) -> str:
    """Render branch selection buttons and return selected branch key."""
    label = "📍 اختر الفرع المرسل" if source_label else "📍 اختر الفرع المصدر"
    st.subheader(label)
    
    render_branch_selection_buttons(session_key, session_key)
    
    info_text = (
        f"📂 من: **{{branch_name}}**" if source_label 
        else f"📂 عرض من: **{{branch_name}}**"
    )
    
    selected = render_selected_branch_info(session_key, info_text)
    st.markdown("---")
    
    return selected


# =============================================================================
# PRIVATE HELPERS: TRANSFERS LOGIC
# =============================================================================

def _render_transfer_tabs(
    csv_dir: str,
    excel_dir: str,
    step: int,
    key_prefix: str,
    selected_branch: str
) -> None:
    """Render tabs for standard transfers browser."""
    tabs = st.tabs(["📊 Excel", "📄 CSV"])
    dirs = [excel_dir, csv_dir]
    exts = [".xlsx", ".csv"]
    branches = get_branches()

    for tab, d, ext in zip(tabs, dirs, exts):
        with tab:
            _process_transfer_tab(
                d, ext, step, key_prefix, selected_branch, branches
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

    files = _collect_transfer_files(directory, ext, sel, branches)
    
    if not files:
        st.warning("لا توجد ملفات")
        return

    files = _filter_transfers(files, sel, branches, kp, ext)
    
    if files:
        _display_transfers(files, kp, sel, ext)


def _collect_transfer_files(
    d: str,
    ext: str,
    sel: str,
    branches: list
) -> list:
    """Collect files based on selected branch."""
    prefix = (
        "transfers_excel_from_" if ext == ".xlsx" 
        else "transfers_from_"
    )
    files = []
    
    target_branches = branches if sel == 'all' else [sel]
    
    for b in target_branches:
        p = os.path.join(d, f"{prefix}{b}_to_other_branches")
        if os.path.exists(p):
            files.extend(list_output_files(p, [ext]))
            
    return files


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
    
    # Prepare zip paths
    for f in files:
        m = re.search(
            r'(from_\w+_to_\w+)', 
            f.get('relative_path', '') + f['name']
        )
        f['zip_path'] = os.path.join(
            m.group(1) if m else 'other', 
            f['name']
        )
        
    # Zip name needs target key if filtered, but we filter inside
    # Logic in original was `tk or 'all'`. We can simplify.
    zip_name = f"{kp}_{sel}_{ext[1:]}.zip"
    render_download_all_button(files, zip_name)
    
    for f in files:
        render_file_expander(f, ext, key_prefix=kp)


# =============================================================================
# PRIVATE HELPERS: MERGED LOGIC
# =============================================================================

def _render_merged_tabs(
    csv_dir: str,
    excel_dir: str,
    step: int,
    kp: str,
    sel: str
) -> None:
    """Render tabs for merged transfers browser."""
    tabs = st.tabs(["📊 Excel", "📄 CSV"])
    dirs = [excel_dir, csv_dir]
    exts = [".xlsx", ".csv"]

    for tab, d, ext in zip(tabs, dirs, exts):
        with tab:
            _process_merged_tab(d, ext, step, kp, sel)


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


# =============================================================================
# PRIVATE HELPERS: SEPARATE LOGIC
# =============================================================================

def _render_separate_tabs(
    csv_dir: str,
    excel_dir: str,
    step: int,
    kp: str,
    sel: str
) -> None:
    """Render tabs for separate transfers browser."""
    tabs = st.tabs(["📊 Excel", "📄 CSV"])
    dirs = [excel_dir, csv_dir]
    exts = [".xlsx", ".csv"]

    for tab, d, ext in zip(tabs, dirs, exts):
        with tab:
            _process_separate_tab(d, ext, step, kp, sel)


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

    # User filters
    tk, ck = _get_separate_filters(kp, ext)
    
    # Collect files
    files = _collect_separate_files(sources, ext, tk, ck)
    
    st.success(f"تم العثور على {len(files)} ملف")
    
    if files:
        _display_separate(files, kp, sel, ext)


def _get_separate_filters(kp: str, ext: str) -> tuple:
    """Render filters for separate files and return keys."""
    branches = get_branches()
    
    # Target Branch Filter
    tgl_opts = ["الكل"] + [BRANCH_LABELS.get(b, b) for b in branches]
    tl = st.selectbox("إلى:", tgl_opts, key=f"{kp}_t_{ext}")
    
    # Category Filter
    cat_opts = ["الكل"] + list(CATEGORY_NAMES.values())
    cl = st.selectbox("الفئة:", cat_opts, key=f"{kp}_c_{ext}")
    
    tk = get_key_from_label(tl, BRANCH_LABELS)
    ck = get_key_from_label(cl, CATEGORY_NAMES)
    
    return tk, ck


def _collect_separate_files(
    sources: list, 
    ext: str, 
    tk: str, 
    ck: str
) -> list:
    """Collect separate files matching filters."""
    files = []
    for src in sources:
        for tgt_name in os.listdir(src['path']):
            tp = os.path.join(src['path'], tgt_name)
            
            # Validation
            if not os.path.isdir(tp):
                continue
            if not tgt_name.startswith('to_'):
                continue
                
            tgt = tgt_name.replace('to_', '')
            if tk and tgt != tk:
                continue
                
            for f in list_files_in_folder(tp, [ext]):
                # Add metadata
                f.update({
                    'source_branch': src['branch'],
                    'target_branch': tgt,
                    'source_folder': src['name'],
                    'target_folder': tgt_name
                })
                
                # Category filter
                if ck and ck not in f['name'].lower():
                    continue
                    
                files.append(f)
    return files


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
