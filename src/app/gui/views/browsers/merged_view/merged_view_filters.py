"""Filtering logic for merged view."""

import streamlit as st
from src.app.gui.utils.translations import CATEGORY_NAMES
from src.app.gui.components import get_key_from_label


def filter_merged_files(files: list, kp: str, ext: str) -> list:
    """Filter merged files by category."""
    cat_opts = ["الكل"] + list(CATEGORY_NAMES.values())
    cat = st.selectbox("الفئة:", cat_opts, key=f"{kp}_c_{ext}")
    ck = get_key_from_label(cat, CATEGORY_NAMES)
    
    if not ck:
        return files
        
    return [f for f in files if ck in f['name'].lower()]
