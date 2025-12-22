"""GUI components package - Re-exports all components for backward compatibility."""

from src.app.gui.components.branch_selection import (
    BRANCH_LABELS,
    get_branch_key_from_label,
    render_branch_selection_buttons,
    render_selected_branch_info
)

from src.app.gui.components.file_display import (
    render_file_expander,
    render_download_all_button
)

from src.app.gui.components.file_grouping import (
    get_key_from_label,
    group_files_by_branch,
    group_files_by_source_target
)

__all__ = [
    'BRANCH_LABELS',
    'get_branch_key_from_label',
    'render_branch_selection_buttons',
    'render_selected_branch_info',
    'render_file_expander',
    'render_download_all_button',
    'get_key_from_label',
    'group_files_by_branch',
    'group_files_by_source_target',
]
