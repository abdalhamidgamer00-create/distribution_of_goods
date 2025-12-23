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
    
    if not by_branch or len(by_branch) <= 1:
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
    
    # Skip filter if only one category (e.g. 'other' for shortage)
    if not by_cat or len(by_cat) <= 1:
        return files

    opts = ["الكل"] + [
        CATEGORY_NAMES.get(c, c) 
        for c in sorted(by_cat)
    ]
    
    selected = st.selectbox("الفئة:", opts, key=f"{key}_c_{ext}")
    
    if selected == "الكل":
        return files
        
    cat_key = get_key_from_label(selected, CATEGORY_NAMES)
    
    # For 'other', we want files that DON'T match known categories
    if cat_key == 'other':
        known_cats = [k for k in CATEGORY_NAMES.keys() if k != 'other']
        return [
            f for f in files 
            if not any(k in f['name'].lower() for k in known_cats)
        ]
        
    return [f for f in files if cat_key in f['name'].lower()]
