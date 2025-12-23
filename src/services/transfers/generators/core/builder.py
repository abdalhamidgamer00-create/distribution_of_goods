"""Transfer DataFrame builder logic."""

import math
import pandas as pd
from src.services.transfers.generators.core import calculation


def build_transfer_dataframe(
    analytics_dataframe: pd.DataFrame, 
    transfer_amounts: pd.Series, 
    target_branch: str
) -> pd.DataFrame:
    """Build transfer DataFrame from valid rows."""
    valid_rows = transfer_amounts > 0
    if not valid_rows.any():
        return None
    
    transfer_dataframe = analytics_dataframe.loc[
        valid_rows, ['code', 'product_name']
    ].copy()
    
    transfer_dataframe['quantity_to_transfer'] = transfer_amounts[
        valid_rows
    ].apply(lambda value: math.ceil(value)).astype(int)
    
    transfer_dataframe['target_branch'] = target_branch
    transfer_dataframe = transfer_dataframe.sort_values(
        'product_name', 
        ascending=True, 
        key=lambda column: column.str.lower()
    )
    return transfer_dataframe


def build_and_validate_transfer(
    analytics_dataframe: pd.DataFrame, 
    source_branch: str, 
    target_branch: str
) -> pd.DataFrame:
    """Build and validate transfer dataframe."""
    transfer_amounts = calculation.calculate_transfer_amounts(
        analytics_dataframe, source_branch
    )
    return build_transfer_dataframe(
        analytics_dataframe, transfer_amounts, target_branch
    )
