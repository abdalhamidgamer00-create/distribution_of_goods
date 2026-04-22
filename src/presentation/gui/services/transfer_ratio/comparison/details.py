"""Detail-frame helpers for transfer ratio comparison."""

from __future__ import annotations

import pandas as pd

from src.presentation.gui.services.transfer_ratio.shared.constants import (
    CODE_ONLY_ASSUMPTION,
    FULL_ASSUMPTION,
)


def prepare_detail_frame(dataframe: pd.DataFrame, side: str) -> pd.DataFrame:
    """Prepare missing detail rows for UI display."""
    columns = {
        f"source_branch_{side}": "source_branch",
        f"target_branch_{side}": "target_branch",
        f"code_{side}": "code",
        f"product_name_{side}": "product_name",
        f"quantity_{side}": "quantity",
    }
    available = [column for column in columns if column in dataframe.columns]
    return dataframe[available].rename(columns=columns).reset_index(drop=True)


def prepare_unexpected_frame(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Prepare unexpected rows for UI display."""
    if dataframe.empty:
        return dataframe
    columns = [
        "source_branch",
        "target_branch",
        "code",
        "product_name",
        "quantity",
    ]
    return dataframe[columns].reset_index(drop=True)


def build_assumptions(code_only_mode: bool) -> str:
    """Return the comparison assumption note shown in the UI."""
    return CODE_ONLY_ASSUMPTION if code_only_mode else FULL_ASSUMPTION
