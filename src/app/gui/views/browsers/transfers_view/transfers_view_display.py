"""Display logic for transfers view."""

import os
import re
import streamlit as st
from src.app.gui.components import (
    render_file_expander,
    render_download_all_button
)


def display_transfer_files(
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
