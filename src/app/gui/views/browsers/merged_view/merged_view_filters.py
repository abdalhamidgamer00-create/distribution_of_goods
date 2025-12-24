"""Filtering logic for merged view."""

from typing import List, Dict
import streamlit as st
from src.app.gui.utils.translations import CATEGORY_NAMES
from src.app.gui.components import get_key_from_label


def filter_merged_files(
    files: List[Dict], 
    key_prefix: str, 
    extension: str
) -> List[Dict]:
    """
    Filter merged files by category.
    
    Args:
        files: List of file metadata dictionaries
        key_prefix: Unique prefix for UI element keys
        extension: File extension (.csv or .xlsx)
        
    Returns:
        Filtered list of files
    """
    category_options = ["الكل"] + list(CATEGORY_NAMES.values())
    selected_category = st.selectbox(
        "الفئة:", 
        category_options, 
        key=f"{key_prefix}_category_{extension}"
    )
    category_key = get_key_from_label(selected_category, CATEGORY_NAMES)
    
    if not category_key:
        return files
        
    return [f for f in files if category_key in f['name'].lower()]
