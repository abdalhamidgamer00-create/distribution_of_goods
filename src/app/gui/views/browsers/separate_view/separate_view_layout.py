"""Main layout for separate transfers view."""

from src.app.gui.components import (
    render_branch_selection_section,
    setup_browser_page,
    render_browser_tabs
)
from src.app.gui.views.browsers.separate_view import separate_view_logic as logic


def render_separate_browser(
    title: str,
    icon: str,
    csv: str,
    excel: str,
    step: int,
    sk: str,
    kp: str
) -> None:
    """Render separate transfers browser."""
    if not setup_browser_page(title, icon):
        return

    selected_branch = render_branch_selection_section(
        session_key=sk,
        subheader_label="📍 اختر الفرع المرسل",
        info_message_template="📂 من: **{branch_name}**"
    )
    
    if not selected_branch:
        return

    render_browser_tabs(
        csv, 
        excel, 
        lambda d, e: logic.process_separate_tab(d, e, step, kp, selected_branch)
    )
