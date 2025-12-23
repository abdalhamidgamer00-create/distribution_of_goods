"""Basic quantity calculations"""

import math
import pandas as pd


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
    df = branch_df.copy()
    monthly = _calculate_monthly(df['avg_sales'])
    
    df['monthly_quantity'] = monthly
    df['surplus_quantity'] = _calculate_surplus(df['balance'], monthly)
    df['needed_quantity'] = _calculate_needed(monthly, df['balance'])
    
    return df


def _calculate_branch_remaining(
    branch_df: pd.DataFrame, branch: str, withdrawals: dict
) -> list:
    """Calculate surplus remaining for a single branch."""
    results = []
    for idx in range(len(branch_df)):
        orig = branch_df.iloc[idx]['surplus_quantity']
        withdrawn = withdrawals.get((branch, idx), 0.0)
        remaining = math.floor(max(0, orig - withdrawn))
        results.append(remaining)
    return results


def calculate_surplus_remaining(
    branches: list, branch_data: dict, withdrawals: dict
) -> dict:
    """Calculate surplus_remaining for each branch based on withdrawals."""
    return {
        b: _calculate_branch_remaining(branch_data[b], b, withdrawals)
        for b in branches
    }
