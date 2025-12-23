"""Tab processing logic for transfers view."""

import os
import streamlit as st
from src.app.gui.services.file_service import collect_transfer_files
from src.app.gui.views.browsers.transfers_view import filters, display


def process_transfer_tab(
    directory: str,
    ext: str,
    step: int,
    kp: str,
    sel: str,
    branches: list
) -> None:
    """Process single tab logic for transfers."""
    if not os.path.exists(directory):
        st.warning(f"يرجى تشغيل الخطوة {step} أولاً.")
        return

    files = collect_transfer_files(directory, ext, sel, branches)
    
    if not files:
        st.warning("لا توجد ملفات")
        return

    files = filters.filter_transfers(files, sel, branches, kp, ext)
    
    if files:
        display.display_transfer_files(files, kp, sel, ext)
