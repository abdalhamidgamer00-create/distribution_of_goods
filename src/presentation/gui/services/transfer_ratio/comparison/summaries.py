"""Compatibility exports for transfer ratio summary helpers."""

from src.presentation.gui.services.transfer_ratio.comparison.aggregation import (
    build_branch_summary,
    build_overall_summary,
    group_rows,
)
from src.presentation.gui.services.transfer_ratio.comparison.details import (
    build_assumptions,
    prepare_detail_frame,
    prepare_unexpected_frame,
)

__all__ = [
    "build_assumptions",
    "build_branch_summary",
    "build_overall_summary",
    "group_rows",
    "prepare_detail_frame",
    "prepare_unexpected_frame",
]
