"""Generic file browser template."""
import streamlit as st
import os
from src.app.gui.utils.file_manager import (
    list_output_files,
    organize_files_by_branch,
    organize_files_by_category
)
from src.app.gui.utils.translations import BRANCH_NAMES, CATEGORY_NAMES, MESSAGES
from src.app.gui.components import (
    render_file_expander,
    render_download_all_button,
    get_key_from_label
)


# =============================================================================
# PUBLIC API
# =============================================================================

def render_simple_browser(
    title: str, 
    icon: str, 
    csv_dir: str, 
    excel_dir: str, 
    step: int, 
    key: str, 
    show_branch: bool = True
) -> None:
    """Render the main simple file browser page structure."""
    _setup_page_config(title, icon)
    
    tabs = st.tabs(["📊 Excel", "📄 CSV"])
    directories = [excel_dir, csv_dir]
    extensions = [".xlsx", ".csv"]
    
    for tab, directory, ext in zip(tabs, directories, extensions):
        with tab:
            _process_directory_tab(directory, ext, step, key, show_branch)


# =============================================================================
# PAGE SETUP HELPERS
# =============================================================================

def _setup_page_config(title: str, icon: str) -> None:
    """Setup page configuration and authentication."""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    
    # Import locally to avoid circular imports
    from src.app.gui.utils.auth import check_password
    if not check_password():
        st.stop()
        
    st.title(f"{icon} {title}")
    st.markdown("---")


# =============================================================================
# TAB PROCESSING HELPERS
# =============================================================================

def _process_directory_tab(
    directory: str, 
    ext: str, 
    step_num: int, 
    key: str, 
    show_branch: bool
) -> None:
    """Process and render content for a single directory tab."""
    if not os.path.exists(directory):
        st.warning(f"يرجى تشغيل الخطوة {step_num} أولاً.")
        return

    files = list_output_files(directory, [ext])
    
    if not files:
        st.info(MESSAGES["no_files"])
        return

    st.success(f"تم العثور على {len(files)} ملف")

    # Apply filters
    filtered_files = files
    if show_branch:
        filtered_files = _filter_files_by_branch(filtered_files, key, ext)
    
    filtered_files = _filter_files_by_category(filtered_files, key, ext)
    
    # Display results
    _render_files_list(filtered_files, ext, key)


# =============================================================================
# FILTERING HELPERS
# =============================================================================

def _filter_files_by_branch(files: list, key: str, ext: str) -> list:
    """Filter files based on selected branch."""
    by_branch = organize_files_by_branch(files)
    
    if not by_branch:
        return files
        
    # Create sorted options list
    opts = ["الكل"] + [BRANCH_NAMES.get(b, b) for b in sorted(by_branch)]
    
    selected = st.selectbox("الفرع:", opts, key=f"{key}_b_{ext}")
    
    if selected == "الكل":
        return files
        
    branch_key = get_key_from_label(selected, BRANCH_NAMES)
    return [f for f in files if branch_key in f['relative_path']]


def _filter_files_by_category(files: list, key: str, ext: str) -> list:
    """Filter files based on selected category."""
    by_cat = organize_files_by_category(files)
    
    if not by_cat:
        return files

    # Create sorted options list
    opts = ["الكل"] + [CATEGORY_NAMES.get(c, c) for c in sorted(by_cat)]
    
    selected = st.selectbox("الفئة:", opts, key=f"{key}_c_{ext}")
    
    if selected == "الكل":
        return files
        
    cat_key = get_key_from_label(selected, CATEGORY_NAMES)
    return [f for f in files if cat_key in f['name'].lower()]


# =============================================================================
# RENDERING HELPERS
# =============================================================================

def _render_files_list(files: list, ext: str, key: str) -> None:
    """Render the list of files with download all button."""
    if not files:
        return

    # Add zip path for bulk download
    for f in files:
        f['zip_path'] = f['relative_path']
        
    render_download_all_button(files, f"{key}_{ext[1:]}.zip")
    
    for f in files:
        render_file_expander(f, ext, key_prefix=key)
