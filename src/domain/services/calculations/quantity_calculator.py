"""Basic quantity calculations"""

import math
import pandas as pd
from src.shared.constants import (
    STOCK_COVERAGE_DAYS, 
    MAX_BALANCE_FOR_NEED_THRESHOLD,
    MIN_COVERAGE_FOR_SMALL_NEED_SUPPRESSION,
    MIN_NEED_THRESHOLD
)


def _calculate_coverage_quantity(avg_sales: pd.Series) -> pd.Series:
    """Calculate target coverage quantity using ceiling."""
    return (avg_sales * STOCK_COVERAGE_DAYS).apply(lambda x: math.ceil(x))


def _calculate_surplus(balance: pd.Series, coverage: pd.Series) -> pd.Series:
    """Calculate surplus quantity using floor."""
    return (balance - coverage).apply(lambda x: max(0, math.floor(x)))


def _calculate_needed(coverage: pd.Series, balance: pd.Series) -> pd.Series:
    """Calculate needed quantity using ceiling."""
    return (coverage - balance).apply(lambda x: max(0, math.ceil(x)))


def calculate_basic_quantities(branch_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate coverage, surplus, and needed quantities."""
    dataframe = branch_df.copy()
    coverage = _calculate_coverage_quantity(dataframe['avg_sales'])
    
    dataframe['coverage_quantity'] = coverage
    dataframe['surplus_quantity'] = _calculate_surplus(
        dataframe['balance'], coverage
    )
    dataframe['needed_quantity'] = _calculate_needed(
        coverage, dataframe['balance']
    )
    
    # New Rule: If balance >= threshold, suppress need to 0
    dataframe.loc[
        dataframe['balance'] >= MAX_BALANCE_FOR_NEED_THRESHOLD, 
        'needed_quantity'
    ] = 0
    
    # New Rule: Small Need Suppression
    # If coverage >= 15 and need < 10, suppress to 0
    small_need_mask = (
        (dataframe['coverage_quantity'] >= MIN_COVERAGE_FOR_SMALL_NEED_SUPPRESSION) &
        (dataframe['needed_quantity'] > 0) & 
        (dataframe['needed_quantity'] < MIN_NEED_THRESHOLD)
    )
    dataframe.loc[small_need_mask, 'needed_quantity'] = 0
    
    return dataframe


def _calculate_branch_remaining(
    branch_df: pd.DataFrame, branch: str, withdrawals: dict
) -> list:
    """Calculate surplus remaining for a single branch."""
    results = []
    for index in range(len(branch_df)):
        original_surplus = branch_df.iloc[index]['surplus_quantity']
        withdrawn = withdrawals.get((branch, index), 0.0)
        remaining = math.floor(max(0, original_surplus - withdrawn))
        results.append(remaining)
    return results


def calculate_surplus_remaining(
    branches: list, branch_data: dict, withdrawals: dict
) -> dict:
    """Calculate surplus_remaining for each branch based on withdrawals."""
    return {
        branch_name: _calculate_branch_remaining(
            branch_data[branch_name], branch_name, withdrawals
        )
        for branch_name in branches
    }
