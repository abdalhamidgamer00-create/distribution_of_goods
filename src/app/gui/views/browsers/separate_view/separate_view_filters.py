"""Filter rendering for separate transfers view."""

import streamlit as st
from src.core.domain.branches.config import get_branches
from src.app.gui.utils.translations import CATEGORY_NAMES
from src.app.gui.components import (
    BRANCH_LABELS,
    get_key_from_label
)


def render_filters(kp: str, ext: str) -> tuple:
    """Render filters for separate files and return keys."""
    branches = get_branches()
    
    tgl_opts = ["الكل"] + [BRANCH_LABELS.get(b, b) for b in branches]
    tl = st.selectbox("إلى:", tgl_opts, key=f"{kp}_t_{ext}")
    
    cat_opts = ["الكل"] + list(CATEGORY_NAMES.values())
    cl = st.selectbox("الفئة:", cat_opts, key=f"{kp}_c_{ext}")
    
    tk = get_key_from_label(tl, BRANCH_LABELS)
    ck = get_key_from_label(cl, CATEGORY_NAMES)
    
    return tk, ck
