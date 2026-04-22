"""Merge and validation helpers for transfer ratio comparison."""

from __future__ import annotations

import pandas as pd

from src.presentation.gui.services.transfer_ratio.comparison.aggregation import (
    build_branch_summary,
)
from src.presentation.gui.services.transfer_ratio.shared.constants import (
    CODE_ONLY_MODE,
    FULL_TRANSFER_KEY,
)


def validate_rows(
    expected_rows: pd.DataFrame,
    actual_rows: pd.DataFrame,
) -> None:
    """Validate that both workbook sides produced comparable rows."""
    if expected_rows.empty:
        raise ValueError("تعذر استخراج بيانات قابلة للمقارنة من الملف الأول.")
    if actual_rows.empty:
        raise ValueError("تعذر استخراج بيانات قابلة للمقارنة من الملف الثاني.")


def merge_grouped(
    expected_grouped: pd.DataFrame,
    actual_grouped: pd.DataFrame,
) -> pd.DataFrame:
    """Merge grouped expected and actual rows into one frame."""
    merged = expected_grouped.merge(
        actual_grouped,
        on="comparison_key",
        how="left",
        suffixes=("_expected", "_actual"),
    ).fillna(_fill_values())
    merged["matched_quantity"] = merged[
        ["quantity_expected", "quantity_actual"]
    ].min(axis=1)
    merged["is_matched"] = merged["quantity_actual"] > 0
    return merged


def branch_frame(merged: pd.DataFrame, code_only_mode: bool) -> pd.DataFrame:
    """Return branch metrics only when branch data exists."""
    return pd.DataFrame() if code_only_mode else build_branch_summary(merged)


def matching_basis(code_only_mode: bool) -> str:
    """Return the UI matching basis label."""
    return CODE_ONLY_MODE if code_only_mode else FULL_TRANSFER_KEY


def _fill_values() -> dict[str, object]:
    return {
        "quantity_actual": 0.0,
        "source_branch_actual": "",
        "target_branch_actual": "",
        "code_actual": "",
        "product_name_actual": "",
    }
