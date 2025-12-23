"""Processing dataframe helpers."""

import pandas as pd
from src.core.domain.calculations.quantity_calculator import (
    calculate_basic_quantities
)
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def create_branch_dataframe(
    dataframe: pd.DataFrame, branch: str, base_columns: list, num_days: int
) -> pd.DataFrame:
    """Create a processed DataFrame for a single branch."""
    branch_columns = [f'{branch}_sales', f'{branch}_balance']
    branch_dataframe = dataframe[base_columns + branch_columns].copy()
    branch_dataframe.columns = base_columns + ['sales', 'balance']
    branch_dataframe['sales'] = pd.to_numeric(
        branch_dataframe['sales'], errors='coerce'
    ).fillna(0.0)
    branch_dataframe['balance'] = pd.to_numeric(
        branch_dataframe['balance'], errors='coerce'
    ).fillna(0.0)
    branch_dataframe['avg_sales'] = branch_dataframe['sales'] / num_days
    return calculate_basic_quantities(branch_dataframe)


def build_branch_data_dict(
    dataframe: pd.DataFrame, branches: list, base_columns: list, num_days: int
) -> dict:
    """Build dictionary of branch DataFrames."""
    branch_data = {}
    for branch in branches:
        branch_data[branch] = create_branch_dataframe(
            dataframe, branch, base_columns, num_days
        )
        msg = f"✅ Calculated avg_sales for {branch}: sales / {num_days} days"
        logger.info(msg)
    
    num_prods = len(branch_data[branches[0]])
    logger.info(
        "Prepared data for %d branches, %d products", 
        len(branches), num_prods
    )
    return branch_data
