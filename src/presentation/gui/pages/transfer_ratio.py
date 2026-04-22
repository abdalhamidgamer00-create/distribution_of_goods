"""Transfer ratio page entry point."""

import os
import sys


project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../..")
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.presentation.gui.views.purchases.transfer_ratio_page import (
    render_transfer_ratio_page,
)


render_transfer_ratio_page()
