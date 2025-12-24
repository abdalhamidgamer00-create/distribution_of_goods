"""Filter rendering for separate transfers view."""

from typing import Tuple, Optional
import streamlit as st
from src.domain.services.branches.config import get_branches
from src.app.gui.utils.translations import CATEGORY_NAMES
from src.app.gui.components import (
    BRANCH_LABELS,
    get_key_from_label
)


def render_filters(
    key_prefix: str, extension: str
) -> Tuple[Optional[str], Optional[str]]:
    """
    Render filters for separate files and return keys.
    
    Args:
        key_prefix: Unique prefix for UI element keys
        extension: File extension (.csv or .xlsx)
        
    Returns:
        Tuple of (target_branch_key, category_key)
    """
    branches_list = get_branches()
    
    target_labels = [BRANCH_LABELS.get(b, b) for b in branches_list]
    target_options = ["الكل"] + target_labels
    selected_target = st.selectbox(
        "إلى:", 
        target_options, 
        key=f"{key_prefix}_target_{extension}"
    )
    
    category_options = ["الكل"] + list(CATEGORY_NAMES.values())
    selected_category = st.selectbox(
        "الفئة:", 
        category_options, 
        key=f"{key_prefix}_category_{extension}"
    )
    
    target_branch_key = get_key_from_label(selected_target, BRANCH_LABELS)
    category_key = get_key_from_label(selected_category, CATEGORY_NAMES)
    
    return target_branch_key, category_key
