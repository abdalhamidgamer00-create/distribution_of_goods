"""Basic quantity calculations"""

import math
import pandas as pd
from src.shared.constants import (
    NEED_COVERAGE_DAYS, SURPLUS_COVERAGE_DAYS, SHORTAGE_COVERAGE_DAYS
)
from src.domain.services.inventory.inventory_policy import InventoryPolicy


def _calculate_target_quantity(avg_sales: pd.Series, days: int) -> pd.Series:
    """Calculate target coverage quantity using ceiling."""
    return (avg_sales * days).apply(lambda x: math.ceil(x))


def _calculate_surplus(balance: pd.Series, target: pd.Series) -> pd.Series:
    """Calculate surplus quantity using floor."""
    return (balance - target).apply(lambda x: max(0, math.floor(x)))


def _calculate_needed(target: pd.Series, balance: pd.Series) -> pd.Series:
    """Calculate needed quantity using ceiling."""
    return (target - balance).apply(lambda x: max(0, math.ceil(x)))


def calculate_basic_quantities(branch_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate surplus(60d), needed(20d) and shortage(30d)."""
    dataframe = branch_df.copy()
    
    # 1. Targets
    surplus_target = _calculate_target_quantity(dataframe['avg_sales'], SURPLUS_COVERAGE_DAYS)
    need_target = _calculate_target_quantity(dataframe['avg_sales'], NEED_COVERAGE_DAYS)
    shortage_target = _calculate_target_quantity(dataframe['avg_sales'], SHORTAGE_COVERAGE_DAYS)

    # 2. Main Logic
    dataframe['surplus_quantity'] = _calculate_surplus(dataframe['balance'], surplus_target)
    dataframe['needed_quantity'] = _calculate_needed(need_target, dataframe['balance'])
    dataframe['shortage_quantity'] = _calculate_needed(shortage_target, dataframe['balance'])
    
    # For compatibility with downstream logic that expects 'coverage_quantity'
    dataframe['coverage_quantity'] = need_target
    
    # 3. Apply business rules to the 'needed_quantity' (transfers)
    return InventoryPolicy.apply_vectorized_rules(dataframe)


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
