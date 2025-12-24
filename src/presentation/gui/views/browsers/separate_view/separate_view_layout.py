"""Main layout for separate transfers view."""

from src.presentation.gui.components import (
    render_branch_selection_section,
    setup_browser_page,
    render_browser_tabs
)
from src.presentation.gui.views.browsers.separate_view import separate_view_logic as logic


def render_separate_browser(
    title: str,
    icon: str,
    csv_directory: str,
    excel_directory: str,
    step_number: int,
    session_key: str,
    key_prefix: str
) -> None:
    """
    Render separate transfers browser.
    
    Args:
        title: Page title
        icon: Page icon
        csv_directory: Directory for CSV files
        excel_directory: Directory for Excel files
        step_number: Pipeline step number
        session_key: Streamlit session state key for branch selection
        key_prefix: Unique prefix for UI element keys
    """
    if not setup_browser_page(title, icon):
        return

    selected_branch = render_branch_selection_section(
        session_key=session_key,
        subheader_label="📍 اختر الفرع المرسل",
        info_message_template="📂 من: **{branch_name}**"
    )
    
    if not selected_branch:
        return

    render_browser_tabs(
        csv_directory, 
        excel_directory, 
        lambda dir_path, ext: logic.process_separate_tab(
            dir_path, 
            ext, 
            step_number, 
            key_prefix, 
            selected_branch
        )
    )
