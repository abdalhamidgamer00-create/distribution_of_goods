"""Main layout for transfers view."""

from functools import partial

from src.domain.services.branches.config import get_branches
from src.presentation.gui.views.browsers.base_browser_layout import render_branch_browser
from src.presentation.gui.views.browsers.transfers_view import transfers_view_logic as logic


def render_transfers_browser(
    title: str,
    icon: str,
    csv_directory: str,
    excel_directory: str,
    step_number: int,
    session_key: str,
    key_prefix: str,
    help_text: str = None,
) -> None:
    """Render transfer files browser with branch selection."""
    branches = get_branches()

    def _tab_callback(dir_path, ext, step_num, prefix, selected):
        logic.process_transfer_tab(
            dir_path, ext, step_num, prefix, selected, branches
        )

    render_branch_browser(
        title=title,
        icon=icon,
        csv_directory=csv_directory,
        excel_directory=excel_directory,
        step_number=step_number,
        session_key=session_key,
        key_prefix=key_prefix,
        tab_callback=_tab_callback,
        subheader_label="📍 اختر الفرع المصدر",
        info_message_template="📂 عرض من: **{branch_name}**",
        help_text=help_text,
    )
