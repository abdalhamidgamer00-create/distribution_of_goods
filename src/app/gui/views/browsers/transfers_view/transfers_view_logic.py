"""Tab processing logic for transfers view."""

import os
import streamlit as st
from src.app.gui.services.file_service import collect_transfer_files
from src.app.gui.views.browsers.transfers_view import transfers_view_filters as filters, transfers_view_display as display


def process_transfer_tab(
    directory: str,
    ext: str,
    step: int,
    kp: str,
    sel: str,
    branches: list
) -> None:
    """Process single tab logic using QueryOutputs use case."""
    from src.app.gui.services.pipeline_service import get_repository
    from src.application.use_cases.query_outputs import QueryOutputs
    
    repository = get_repository()
    use_case = QueryOutputs(repository)
    
    # Get standard transfer outputs for current source branch
    files = use_case.execute('transfers', sel)
    
    # Filter by extension
    files = [f for f in files if f['name'].endswith(ext)]
    
    if not files:
        st.warning("لا توجد ملفات")
        return

    # Add relative_path key for compatibility with display
    for f in files:
        if 'relative_path' not in f:
            f['relative_path'] = f['path']

    files = filters.filter_transfers(files, sel, branches, kp, ext)
    
    if files:
        display.display_transfer_files(files, kp, sel, ext)
