import streamlit as st
from src.app.gui.views.browsers.separate_view import filters, display


def process_separate_tab(
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
    
    tk, ck = filters.render_filters(kp, ext)
    
    # Get all separate outputs for current source branch
    files = use_case.execute('separate', sel)
    
    # Filter by extension, target, and category
    files = [f for f in files if f['name'].endswith(ext)]
    
    if tk:
        files = [f for f in files if f.get('target_branch') == tk]
    if ck:
        files = [f for f in files if ck in f.get('product_category', '')]
        
    if not files:
        st.info("لا توجد ملفات")
        return

    # Add extra keys for compatibility with display
    for f in files:
        f['relative_path'] = f.get('relative_path', f['path'])
        f['source_branch'] = f.get('source_branch', f.get('branch', sel))
        # Ensure 'source_folder' and 'target_folder' are present (from repository)

    st.success(f"تم العثور على {len(files)} ملف")
    
    if files:
        display.display_separate_files(files, kp, sel, ext)
