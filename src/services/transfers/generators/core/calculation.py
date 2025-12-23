"""Transfer amount calculation logic."""

import pandas as pd
from src.shared.dataframes.validators import clean_numeric_series


def process_transfer_column(
    analytics_dataframe: pd.DataFrame, 
    source_branch: str, 
    column_number: int
) -> pd.Series:
    """Process a single transfer column pair and return amounts."""
    available_column = f'available_branch_{column_number}'
    surplus_column = f'surplus_from_branch_{column_number}'
    if (available_column not in analytics_dataframe.columns or 
            surplus_column not in analytics_dataframe.columns):
        return pd.Series(0.0, index=analytics_dataframe.index)
    
    available_series = analytics_dataframe[
        available_column
    ].fillna("").astype(str).str.strip()
    mask = available_series.eq(source_branch)
    return clean_numeric_series(
        analytics_dataframe[surplus_column]
    ).where(mask, 0.0)


def calculate_transfer_amounts(
    analytics_dataframe: pd.DataFrame, 
    source_branch: str
) -> pd.Series:
    """Calculate transfer amounts from source branch columns."""
    transfer_amounts = pd.Series(0.0, index=analytics_dataframe.index)
    for column_number in range(1, 10):
        transfer_amounts += process_transfer_column(
            analytics_dataframe, source_branch, column_number
        )
    return transfer_amounts
