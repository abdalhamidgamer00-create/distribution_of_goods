"""Finalization helpers for normalized workbook sheets."""

from __future__ import annotations

import pandas as pd

from src.presentation.gui.services.transfer_ratio.shared.constants import (
    CODE_ONLY_MODE,
)
from src.presentation.gui.services.transfer_ratio.shared.keys import build_key
from src.presentation.gui.services.transfer_ratio.shared.text_utils import (
    normalize_header,
)


def finalize_normalized_frame(normalized: pd.DataFrame) -> pd.DataFrame:
    """Finish normalized rows by adding match keys and final columns."""
    normalized["match_token"] = normalized["code"]
    blank_codes = normalized["match_token"] == ""
    normalized.loc[blank_codes, "match_token"] = normalized.loc[
        blank_codes, "product_name"
    ].map(normalize_header)
    normalized = normalized[normalized["match_token"] != ""].copy()
    normalized["comparison_key"] = normalized.apply(_comparison_key, axis=1)
    return normalized[_final_columns()]


def _comparison_key(row) -> str:
    return build_key(
        row,
        code_only_mode=(row["comparison_mode"] == CODE_ONLY_MODE),
    )


def _final_columns() -> list[str]:
    return [
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
