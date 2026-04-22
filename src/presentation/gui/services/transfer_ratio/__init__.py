"""Public API for transfer ratio comparison services."""

from src.presentation.gui.services.transfer_ratio.comparison.comparison import (
    compare_transfer_workbooks,
    compare_transfer_workbook_sets,
)
from src.presentation.gui.services.transfer_ratio.shared.models import (
    WorkbookComparison,
)

__all__ = [
    "WorkbookComparison",
    "compare_transfer_workbooks",
    "compare_transfer_workbook_sets",
]
