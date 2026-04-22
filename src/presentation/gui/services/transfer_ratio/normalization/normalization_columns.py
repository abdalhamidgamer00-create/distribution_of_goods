"""Column and value helpers for sheet normalization."""

from __future__ import annotations

import pandas as pd

from src.presentation.gui.services.transfer_ratio.shared.columns import (
    find_column,
)
from src.presentation.gui.services.transfer_ratio.shared.constants import (
    COLUMN_ALIASES,
)
from src.presentation.gui.services.transfer_ratio.shared.text_utils import (
    clean_text,
)


def detect_columns(sheet: pd.DataFrame) -> dict[str, str | None]:
    """Detect supported logical columns in a workbook sheet."""
    return {
        key: find_column(sheet.columns, aliases)
        for key, aliases in COLUMN_ALIASES.items()
    }


def string_series(sheet: pd.DataFrame, column: str | None) -> pd.Series:
    """Return a clean string series for a logical column."""
    if column:
        return sheet[column].map(clean_text)
    return pd.Series("", index=sheet.index)


def quantity_series(sheet: pd.DataFrame, column: str | None) -> pd.Series:
    """Return a numeric quantity series with safe defaults."""
    if column is None:
        return pd.Series(1.0, index=sheet.index)
    return pd.to_numeric(sheet[column], errors="coerce").fillna(1.0)
