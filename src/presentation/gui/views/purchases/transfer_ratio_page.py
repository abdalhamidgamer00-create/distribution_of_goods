"""Transfer ratio page orchestration."""

from src.presentation.gui.components.browser_shared import setup_browser_page
from src.presentation.gui.views.purchases.transfer_ratio_inputs import (
    render_upload_section,
    run_comparison,
)
from src.presentation.gui.views.purchases.transfer_ratio_labels import (
    PAGE_DESCRIPTION,
    PAGE_ICON,
    PAGE_TITLE,
)
from src.presentation.gui.views.purchases.transfer_ratio_results import (
    render_back_button,
    render_comparison_result,
)


def render_transfer_ratio_page() -> None:
    """Render the full transfer ratio page."""
    setup_browser_page(PAGE_TITLE, PAGE_ICON, PAGE_DESCRIPTION)
    expected_files, actual_files = render_upload_section()
    run_comparison(expected_files, actual_files)
    render_comparison_result()
    render_back_button()
