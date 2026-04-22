"""Sheet normalization for transfer ratio workbooks."""

from __future__ import annotations

import pandas as pd

from src.presentation.gui.services.transfer_ratio.normalization.normalization_columns import (
    detect_columns,
)
from src.presentation.gui.services.transfer_ratio.normalization.normalization_finalize import (
    finalize_normalized_frame,
)
from src.presentation.gui.services.transfer_ratio.normalization.normalization_helpers import (
    build_normalized_frame,
)
from src.presentation.gui.services.transfer_ratio.shared.text_utils import (
    normalize_header,
)


def normalize_sheet(
    dataframe: pd.DataFrame,
    file_name: str,
    sheet_name: str,
    allow_code_only: bool = False,
) -> pd.DataFrame:
    """Normalize a single sheet into a comparison-ready table."""
    if dataframe is None or dataframe.empty:
        return pd.DataFrame()
    sheet = dataframe.copy()
    sheet.columns = [normalize_header(column) for column in sheet.columns]
    columns = detect_columns(sheet)
    if columns["code"] is None and columns["product_name"] is None:
        return pd.DataFrame()
    normalized = build_normalized_frame(
        sheet,
        columns,
        file_name,
        sheet_name,
        allow_code_only,
    )
    return finalize_normalized_frame(normalized)
