"""GUI components package."""
from src.presentation.gui.components.branch_selection import (
    BRANCH_LABELS,
    get_branch_key_from_label,
    render_branch_selection_buttons,
    render_selected_branch_info,
    render_branch_selection_section
)

from src.presentation.gui.components.file_display import (
    render_file_expander,
    render_download_all_button
)

from src.presentation.gui.components.file_grouping import (
    get_key_from_label,
    group_files_by_branch,
    group_files_by_source_target
)
from src.presentation.gui.components.browser_shared import (
    setup_browser_page,
    handle_branch_selection,
    render_browser_tabs
)

__all__ = [
    'BRANCH_LABELS',
    'get_branch_key_from_label',
    'render_branch_selection_buttons',
    'render_selected_branch_info',
    'render_branch_selection_section',
    'render_file_expander',
    'render_download_all_button',
    'get_key_from_label',
    'group_files_by_branch',
    'group_files_by_source_target',
    'setup_browser_page',
    'handle_branch_selection',
    'render_browser_tabs'
]
