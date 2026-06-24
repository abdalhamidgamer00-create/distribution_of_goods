"""Transfer ratio page entry point."""

import src.presentation.gui.page_setup  # noqa: F401  -- path bootstrap

from src.presentation.gui.views.purchases.transfer_ratio_page import (
    render_transfer_ratio_page,
)

render_transfer_ratio_page()
