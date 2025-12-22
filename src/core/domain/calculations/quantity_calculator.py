"""Basic quantity calculations"""

import pandas as pd
import math


def _calculate_monthly(avg_sales: pd.Series) -> pd.Series:
    """Calculate monthly quantity using ceiling."""
    return (avg_sales * 30).apply(lambda x: math.ceil(x))


def _calculate_surplus(balance: pd.Series, monthly: pd.Series) -> pd.Series:
    """Calculate surplus quantity using floor."""
    return (balance - monthly).apply(lambda x: max(0, math.floor(x)))


def _calculate_needed(monthly: pd.Series, balance: pd.Series) -> pd.Series:
    """Calculate needed quantity using ceiling."""
    return (monthly - balance).apply(lambda x: max(0, math.ceil(x)))


def calculate_basic_quantities(branch_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly, surplus, and needed quantities."""
    branch_df = branch_df.copy()
    branch_df['monthly_quantity'] = _calculate_monthly(branch_df['avg_sales'])
    branch_df['surplus_quantity'] = _calculate_surplus(branch_df['balance'], branch_df['monthly_quantity'])
    branch_df['needed_quantity'] = _calculate_needed(branch_df['monthly_quantity'], branch_df['balance'])
    return branch_df


def _calculate_branch_remaining(branch_df: pd.DataFrame, branch: str, withdrawals: dict) -> list:
    """Calculate surplus remaining for a single branch."""
    surplus_remaining_list = []
    for idx in range(len(branch_df)):
        original_surplus = branch_df.iloc[idx]['surplus_quantity']
        withdrawn = withdrawals.get((branch, idx), 0.0)
        remaining = math.floor(max(0, original_surplus - withdrawn))
        surplus_remaining_list.append(remaining)
    return surplus_remaining_list


def calculate_surplus_remaining(branches: list, branch_data: dict, withdrawals: dict) -> dict:
    """Calculate surplus_remaining for each branch based on withdrawals."""
    return {
        branch: _calculate_branch_remaining(branch_data[branch], branch, withdrawals)
        for branch in branches
    }

