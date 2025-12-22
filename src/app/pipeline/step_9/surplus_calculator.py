"""Surplus calculator module

Calculates remaining surplus for each branch after all withdrawals.
"""

import os
import pandas as pd
from src.core.domain.branches.config import get_branches
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_9.analytics_reader import (
    read_analytics_file,
    get_latest_analytics_path,
    extract_withdrawals_from_branch,
)

logger = get_logger(__name__)


# =============================================================================
# PUBLIC API
# =============================================================================

def calculate_total_withdrawals(analytics_dir: str, branch: str) -> dict:
    """Calculate total withdrawals FROM a specific branch across all analytics files."""
    total_withdrawals = {}
    
    for other_branch in get_branches():
        _process_branch_withdrawals(analytics_dir, other_branch, branch, total_withdrawals)
    
    return total_withdrawals


def calculate_remaining_surplus(dataframe: pd.DataFrame, total_withdrawals: dict) -> pd.DataFrame:
    """Calculate remaining surplus for each product."""
    dataframe = dataframe.copy()
    dataframe['total_withdrawn'] = dataframe['code'].astype(str).map(total_withdrawals).fillna(0.0)
    dataframe['calculated_remaining'] = dataframe['surplus_quantity'] - dataframe['total_withdrawn']
    return _filter_and_sort_remaining(dataframe)


def validate_analytics_columns(dataframe: pd.DataFrame) -> list:
    """Validate that required columns exist, return missing column names."""
    required_columns = ['code', 'product_name', 'surplus_quantity']
    return [column for column in required_columns if column not in dataframe.columns]


# =============================================================================
# WITHDRAWAL PROCESSING HELPERS
# =============================================================================

def _process_branch_withdrawals(analytics_dir: str, other_branch: str, source_branch: str, 
                                  total_withdrawals: dict) -> None:
    """Process withdrawals from a single analytics file."""
    analytics_path = get_latest_analytics_path(analytics_dir, other_branch)
    if not analytics_path:
        return
    dataframe, _, _ = read_analytics_file(analytics_path)
    if dataframe is None:
        return
    for product_code, amount in extract_withdrawals_from_branch(dataframe, source_branch).items():
        total_withdrawals[product_code] = total_withdrawals.get(product_code, 0.0) + amount


# =============================================================================
# FILTERING HELPERS
# =============================================================================

def _filter_and_sort_remaining(dataframe) -> pd.DataFrame:
    """Filter products with remaining surplus and sort by name."""
    remaining_dataframe = dataframe[dataframe['calculated_remaining'] > 0].copy()
    if remaining_dataframe.empty:
        return pd.DataFrame(columns=['code', 'product_name', 'surplus_remaining'])
    result_dataframe = pd.DataFrame({
        'code': remaining_dataframe['code'], 
        'product_name': remaining_dataframe['product_name'], 
        'surplus_remaining': remaining_dataframe['calculated_remaining'].astype(int)
    })
    return result_dataframe.sort_values('product_name', ascending=True, key=lambda column: column.str.lower())
