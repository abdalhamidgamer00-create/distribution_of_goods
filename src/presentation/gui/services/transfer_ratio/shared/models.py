"""Data models for transfer ratio comparison results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import pandas as pd


@dataclass(frozen=True)
class WorkbookComparison:
    """Structured comparison output for the transfer ratio page."""

    overall: Dict[str, float]
    by_branch: pd.DataFrame
    missing: pd.DataFrame
    unexpected: pd.DataFrame
    expected_rows: pd.DataFrame
    actual_rows: pd.DataFrame
    assumptions: str
    matching_basis: str
    supports_branch_breakdown: bool
