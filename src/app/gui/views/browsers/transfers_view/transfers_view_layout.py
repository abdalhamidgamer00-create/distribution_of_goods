"""Main layout for transfers view."""

from src.core.domain.branches.config import get_branches
from src.app.gui.components import (
    render_branch_selection_section,
    setup_browser_page,
    render_browser_tabs
)
from src.app.gui.views.browsers.transfers_view import transfers_view_logic as logic


def render_transfers_browser(
    title: str,
    icon: str,
    csv: str,
    excel: str,
    step: int,
    sk: str,
    kp: str
) -> None:
    """Render transfer files browser with branch selection."""
    if not setup_browser_page(title, icon):
        return
    
    selected_branch = render_branch_selection_section(
        session_key=sk,
        subheader_label="📍 اختر الفرع المصدر",
        info_message_template="📂 عرض من: **{branch_name}**"
    )

    if not selected_branch:
        return

    branches = get_branches()
    render_browser_tabs(
        csv, 
        excel,
        lambda d, e: logic.process_transfer_tab(
            d, e, step, kp, selected_branch, branches
        )
    )
