"""Compatibility facade for transfer ratio comparison services."""

from src.presentation.gui.services.transfer_ratio import (
    WorkbookComparison,
    compare_transfer_workbooks,
    compare_transfer_workbook_sets,
)

__all__ = [
    "WorkbookComparison",
    "compare_transfer_workbooks",
    "compare_transfer_workbook_sets",
]
