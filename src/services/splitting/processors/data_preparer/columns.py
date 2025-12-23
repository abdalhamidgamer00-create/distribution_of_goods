"""Column validation helpers."""

import pandas as pd


def validate_required_columns(
    dataframe: pd.DataFrame, branches: list, base_columns: list
) -> None:
    """Validate that all required columns exist in the DataFrame."""
    required_columns = set(base_columns)
    for branch in branches:
        required_columns.update([f'{branch}_sales', f'{branch}_balance'])
    
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
