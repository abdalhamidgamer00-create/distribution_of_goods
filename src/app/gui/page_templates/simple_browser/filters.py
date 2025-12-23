"""UI filtering logic."""

import streamlit as st
from src.app.gui.services.file_service import (
    group_files_by_branch,
    group_files_by_category
)
from src.app.gui.utils.translations import (
    BRANCH_NAMES, 
    CATEGORY_NAMES, 
)
from src.app.gui.components import get_key_from_label


def filter_files_by_branch(files: list, key: str, ext: str) -> list:
    """Filter files based on selected branch."""
    by_branch = group_files_by_branch(files)
    
    if not by_branch:
        return files
        
    opts = ["الكل"] + [
        BRANCH_NAMES.get(b, b) 
        for b in sorted(by_branch)
    ]
    
    selected = st.selectbox("الفرع:", opts, key=f"{key}_b_{ext}")
    
    if selected == "الكل":
        return files
        
    branch_key = get_key_from_label(selected, BRANCH_NAMES)
    return [f for f in files if branch_key in f['relative_path']]


def filter_files_by_category(files: list, key: str, ext: str) -> list:
    """Filter files based on selected category."""
    by_cat = group_files_by_category(files)
    
    if not by_cat:
        return files

    opts = ["الكل"] + [
        CATEGORY_NAMES.get(c, c) 
        for c in sorted(by_cat)
    ]
    
    selected = st.selectbox("الفئة:", opts, key=f"{key}_c_{ext}")
    
    if selected == "الكل":
        return files
        
    cat_key = get_key_from_label(selected, CATEGORY_NAMES)
    return [f for f in files if cat_key in f['name'].lower()]
