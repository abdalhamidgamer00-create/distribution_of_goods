"""Workbook loading helpers for transfer ratio services."""

from __future__ import annotations

import pandas as pd

from src.presentation.gui.services.transfer_ratio.normalization.normalization import (
    normalize_sheet,
)
from src.presentation.gui.services.transfer_ratio.shared.text_utils import (
    extract_name,
)


def load_workbooks(files, allow_code_only: bool = False) -> pd.DataFrame:
    """Load and concatenate multiple workbook inputs."""
    normalized_frames = []
    for file_obj, file_name in files:
        normalized = load_workbook(file_obj, file_name, allow_code_only)
        if not normalized.empty:
            normalized_frames.append(normalized)
    if not normalized_frames:
        return pd.DataFrame()
    return pd.concat(normalized_frames, ignore_index=True)


def load_workbook(
    file_obj,
    file_name,
    allow_code_only: bool = False,
) -> pd.DataFrame:
    """Read all workbook sheets and normalize them into one table."""
    if hasattr(file_obj, "seek"):
        file_obj.seek(0)
    workbook = pd.read_excel(file_obj, sheet_name=None)
    normalized_sheets = _normalized_sheets(
        workbook,
        file_name or extract_name(file_obj),
        allow_code_only,
    )
    if not normalized_sheets:
        return _empty_frame()
    return pd.concat(normalized_sheets, ignore_index=True)


def _normalized_sheets(
    workbook: dict[str, pd.DataFrame],
    file_name: str,
    allow_code_only: bool,
) -> list[pd.DataFrame]:
    normalized_sheets = []
    for sheet_name, dataframe in workbook.items():
        normalized = normalize_sheet(
            dataframe,
            file_name,
            sheet_name,
            allow_code_only,
        )
        if not normalized.empty:
            normalized_sheets.append(normalized)
    return normalized_sheets


def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "source_branch",
            "target_branch",
            "code",
            "product_name",
            "quantity",
            "comparison_key",
            "comparison_mode",
            "sheet_name",
            "file_name",
        ]
    )
