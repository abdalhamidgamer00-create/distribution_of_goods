"""Tab processing logic for separate transfers view."""

import os
import streamlit as st
from src.app.gui.services.file_service import (
    get_matching_folders,
    collect_separate_files
)
from src.app.gui.views.browsers.separate_view import filters, display


def process_separate_tab(
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

    tk, ck = filters.render_filters(kp, ext)
    files = collect_separate_files(sources, ext, tk, ck)
    
    st.success(f"تم العثور على {len(files)} ملف")
    
    if files:
        display.display_separate_files(files, kp, sel, ext)
