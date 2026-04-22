"""Intermediate frame builders for workbook sheet normalization."""

from __future__ import annotations

import pandas as pd

from src.presentation.gui.services.transfer_ratio.normalization.normalization_branches import (
    assign_branches,
    is_code_only,
)
from src.presentation.gui.services.transfer_ratio.normalization.normalization_columns import (
    quantity_series,
    string_series,
)
from src.presentation.gui.services.transfer_ratio.shared.constants import (
    CODE_ONLY_MODE,
    FULL_MODE,
)


def build_normalized_frame(
    sheet: pd.DataFrame,
    columns: dict[str, str | None],
    file_name: str,
    sheet_name: str,
    allow_code_only: bool,
) -> pd.DataFrame:
    """Build the normalized intermediate frame for one sheet."""
    code_only_mode = is_code_only(
        columns,
        allow_code_only,
        file_name,
        sheet_name,
    )
    normalized = pd.DataFrame()
    normalized["code"] = string_series(sheet, columns["code"])
    normalized["product_name"] = string_series(sheet, columns["product_name"])
    normalized["quantity"] = quantity_series(sheet, columns["quantity"])
    assign_branches(
        normalized,
        sheet,
        columns,
        file_name,
        sheet_name,
        code_only_mode,
    )
    normalized["sheet_name"] = sheet_name
    normalized["file_name"] = file_name
    normalized["comparison_mode"] = (
        CODE_ONLY_MODE if code_only_mode else FULL_MODE
    )
    return normalized
