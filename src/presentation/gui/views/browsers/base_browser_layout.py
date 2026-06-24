"""Shared browser layout for merged, separate, and transfers views.

Consolidates the repeated setup -> branch selection -> tabs pattern.
"""

from typing import Callable

from src.presentation.gui.components import (
    render_branch_selection_section,
    setup_browser_page,
    render_browser_tabs,
)


def render_branch_browser(
    title: str,
    icon: str,
    csv_directory: str,
    excel_directory: str,
    step_number: int,
    session_key: str,
    key_prefix: str,
    tab_callback: Callable[[str, str, int, str, str], None],
    subheader_label: str = "📍 اختر الفرع المرسل",
    info_message_template: str = "📂 من: **{branch_name}**",
    help_text: str = None,
) -> None:
    """Render a branch-scoped file browser with CSV/Excel tabs.

    *tab_callback* receives ``(dir_path, ext, step_number, key_prefix,
    selected_branch)`` and should render content for one tab.
    """
    if not setup_browser_page(title, icon, help_text):
        return

    selected_branch = render_branch_selection_section(
        session_key=session_key,
        subheader_label=subheader_label,
        info_message_template=info_message_template,
    )

    if not selected_branch:
        return

    render_browser_tabs(
        csv_directory,
        excel_directory,
        lambda dir_path, ext: tab_callback(
            dir_path, ext, step_number, key_prefix, selected_branch
        ),
    )
