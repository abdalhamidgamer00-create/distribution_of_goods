"""Aggregation helpers for transfer ratio comparison."""

from __future__ import annotations

from typing import Dict

import pandas as pd

from src.presentation.gui.services.transfer_ratio.shared.keys import build_key
from src.presentation.gui.services.transfer_ratio.shared.text_utils import (
    to_percentage,
)


def group_rows(
    dataframe: pd.DataFrame,
    code_only_mode: bool = False,
) -> pd.DataFrame:
    """Aggregate duplicate rows into a single comparison row."""
    working_frame = _working_frame(dataframe, code_only_mode)
    return (
        working_frame.groupby("comparison_key", as_index=False)
        .agg(_aggregation_rules())
        .rename(columns={"quantity": "quantity"})
    )


def build_overall_summary(merged: pd.DataFrame) -> Dict[str, float]:
    """Compute overall item and quantity coverage."""
    expected_items = int(len(merged))
    matched_items = int(merged["is_matched"].sum())
    expected_quantity = float(merged["quantity_expected"].sum())
    matched_quantity = float(merged["matched_quantity"].sum())
    return {
        "expected_items": expected_items,
        "matched_items": matched_items,
        "missing_items": max(0, expected_items - matched_items),
        "item_ratio": to_percentage(matched_items, expected_items),
        "expected_quantity": expected_quantity,
        "matched_quantity": matched_quantity,
        "quantity_ratio": to_percentage(matched_quantity, expected_quantity),
    }


def build_branch_summary(merged: pd.DataFrame) -> pd.DataFrame:
    """Create per-source-branch coverage metrics."""
    branch_frame = merged.assign(
        source_branch_expected=merged["source_branch_expected"].replace(
            "", "unassigned"
        )
    )
    summary = _branch_aggregate(branch_frame)
    summary["missing_items"] = (
        summary["expected_items"] - summary["matched_items"]
    )
    summary["item_ratio"] = summary.apply(_branch_item_ratio, axis=1)
    summary["quantity_ratio"] = summary.apply(_branch_quantity_ratio, axis=1)
    return summary.sort_values(
        ["item_ratio", "quantity_ratio", "source_branch"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def _working_frame(
    dataframe: pd.DataFrame,
    code_only_mode: bool,
) -> pd.DataFrame:
    working_frame = dataframe.copy()
    if not code_only_mode:
        return working_frame
    working_frame["source_branch"] = ""
    working_frame["target_branch"] = ""
    working_frame["comparison_key"] = working_frame.apply(
        lambda row: build_key(row, code_only_mode=True),
        axis=1,
    )
    return working_frame


def _aggregation_rules() -> dict[str, str]:
    return {
        "source_branch": "first",
        "target_branch": "first",
        "code": "first",
        "product_name": "first",
        "quantity": "sum",
    }


def _branch_aggregate(branch_frame: pd.DataFrame) -> pd.DataFrame:
    return (
        branch_frame.groupby("source_branch_expected", as_index=False)
        .agg(
            expected_items=("comparison_key", "count"),
            matched_items=("is_matched", "sum"),
            expected_quantity=("quantity_expected", "sum"),
            matched_quantity=("matched_quantity", "sum"),
        )
        .rename(columns={"source_branch_expected": "source_branch"})
    )


def _branch_item_ratio(row: pd.Series) -> float:
    return to_percentage(row["matched_items"], row["expected_items"])


def _branch_quantity_ratio(row: pd.Series) -> float:
    return to_percentage(row["matched_quantity"], row["expected_quantity"])
