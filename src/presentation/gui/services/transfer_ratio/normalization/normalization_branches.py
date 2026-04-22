"""Branch helpers for sheet normalization."""

from __future__ import annotations

import pandas as pd

from src.presentation.gui.services.transfer_ratio.shared.branching import (
    infer_branch_from_text,
    normalize_branch_name,
)


def is_code_only(
    columns: dict[str, str | None],
    allow_code_only: bool,
    file_name: str,
    sheet_name: str,
) -> bool:
    """Return whether the sheet should compare by code only."""
    has_branch_columns = columns["source_branch"] or columns["target_branch"]
    if not allow_code_only:
        return False
    if has_branch_columns:
        return False
    return not _has_inferred_branch(file_name, sheet_name)


def assign_branches(
    normalized: pd.DataFrame,
    sheet: pd.DataFrame,
    columns: dict[str, str | None],
    file_name: str,
    sheet_name: str,
    code_only_mode: bool,
) -> None:
    """Assign source and target branches to the normalized frame."""
    if code_only_mode:
        normalized["source_branch"] = ""
        normalized["target_branch"] = ""
        return
    normalized["source_branch"] = branch_series(
        sheet,
        columns["source_branch"],
        file_name,
        sheet_name,
        "source",
    )
    normalized["target_branch"] = branch_series(
        sheet,
        columns["target_branch"],
        file_name,
        sheet_name,
        "target",
    )


def branch_series(
    sheet: pd.DataFrame,
    column: str | None,
    file_name: str,
    sheet_name: str,
    branch_role: str,
) -> pd.Series:
    """Return a normalized branch series with filename fallback."""
    fallback = infer_branch_from_text(file_name, sheet_name, branch_role)
    if column is None:
        return pd.Series(fallback, index=sheet.index)
    series = sheet[column].map(normalize_branch_name)
    return series.replace("", fallback) if fallback else series


def _has_inferred_branch(file_name: str, sheet_name: str) -> bool:
    source_branch = infer_branch_from_text(file_name, sheet_name, "source")
    target_branch = infer_branch_from_text(file_name, sheet_name, "target")
    return bool(source_branch or target_branch)
