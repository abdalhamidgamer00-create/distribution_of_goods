import streamlit as st
from src.app.gui.views.browsers.merged_view import filters, display


def process_merged_tab(
    directory: str,
    ext: str,
    step: int,
    kp: str,
    sel: str
) -> None:
    """Process single tab logic using QueryOutputs use case."""
    from src.app.gui.services.pipeline_service import get_repository
    from src.application.use_cases.query_outputs import QueryOutputs
    
    repository = get_repository()
    use_case = QueryOutputs(repository)
    
    # Get all merged outputs for selected branch
    files = use_case.execute('merged', sel)
    
    # Filter by extension
    files = [f for f in files if f['name'].endswith(ext)]
    
    if not files:
        st.info("لا توجد ملفات")
        return

    # Add extra keys for compatibility with filters and display
    for f in files:
        f['relative_path'] = f.get('relative_path', f['path'])
        # folder_name is already in f from repository

    files = filters.filter_merged_files(files, kp, ext)
    
    st.success(f"تم العثور على {len(files)} ملف")
    
    if files:
        display.display_merged_files(files, kp, sel, ext)
