"""Main layout for merged view."""

from src.presentation.gui.views.browsers.base_browser_layout import render_branch_browser
from src.presentation.gui.views.browsers.merged_view import merged_view_logic as logic


def render_merged_browser(
    title: str,
    icon: str,
    csv_directory: str,
    excel_directory: str,
    step_number: int,
    session_key: str,
    key_prefix: str,
    help_text: str = None,
) -> None:
    """Render merged transfers browser."""
    render_branch_browser(
        title=title,
        icon=icon,
        csv_directory=csv_directory,
        excel_directory=excel_directory,
        step_number=step_number,
        session_key=session_key,
        key_prefix=key_prefix,
        tab_callback=logic.process_merged_tab,
        help_text=help_text,
    )
