"""Tab processing logic for merged view."""

import os
import streamlit as st
from src.app.gui.services.file_service import get_matching_folders
from src.app.gui.views.browsers.merged_view import collection, filters, display


def process_merged_tab(
    directory: str,
    ext: str,
    step: int,
    kp: str,
    sel: str
) -> None:
    """Process single tab logic for merged transfers."""
    if not os.path.exists(directory):
        st.warning(f"يرجى تشغيل الخطوة {step} أولاً.")
        return

    folders = get_matching_folders(
        directory, 'combined_transfers_from_', sel
    )
    
    if not folders:
        st.info("لا توجد ملفات")
        return

    files = collection.collect_merged_files(folders, ext)
    files = filters.filter_merged_files(files, kp, ext)
    
    st.success(f"تم العثور على {len(files)} ملف")
    
    if files:
        display.display_merged_files(files, kp, sel, ext)
