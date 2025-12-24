"""Filtering logic for transfers view."""

import streamlit as st
from src.app.gui.components import (
    BRANCH_LABELS,
    get_branch_key_from_label
)


def filter_transfers(
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
