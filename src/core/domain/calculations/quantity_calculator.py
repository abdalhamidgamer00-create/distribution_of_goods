"""Basic quantity calculations"""

import pandas as pd
import math


def calculate_basic_quantities(branch_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate monthly_quantity, surplus_quantity, and needed_quantity
    Using ceiling to ensure whole numbers for drug quantities
    
    Args:
        branch_df: Branch dataframe with sales, avg_sales, and balance columns
        
    Returns:
        DataFrame with calculated quantities added (all as integers)
    """
    branch_df = branch_df.copy()
    # استخدام ceil لتقريب monthly_quantity للأعلى
    branch_df['monthly_quantity'] = (branch_df['avg_sales'] * 30).apply(lambda x: math.ceil(x))
    
    # استخدام floor لتقريب surplus_quantity للأسفل
    branch_df['surplus_quantity'] = (branch_df['balance'] - branch_df['monthly_quantity']).apply(
        lambda x: max(0, math.floor(x))
    )
    
    # استخدام ceil لتقريب needed_quantity للأعلى
    branch_df['needed_quantity'] = (branch_df['monthly_quantity'] - branch_df['balance']).apply(
        lambda x: max(0, math.ceil(x))
    )
    
    return branch_df


def calculate_surplus_remaining(branches: list, branch_data: dict, withdrawals: dict) -> dict:
    """
    Calculate surplus_remaining for each branch based on withdrawals
    Using floor to ensure whole numbers
    
    Args:
        branches: List of branch names
        branch_data: Dictionary of all branch dataframes
        withdrawals: Dictionary mapping (branch, idx) to amount withdrawn
        
    Returns:
        Dictionary mapping branch name to list of surplus_remaining values (all as integers)
    """
    surplus_remaining_dict = {}
    
    for branch in branches:
        branch_df = branch_data[branch]
        surplus_remaining_list = []
        
        for idx in range(len(branch_df)):
            original_surplus = branch_df.iloc[idx]['surplus_quantity']
            withdrawn = withdrawals.get((branch, idx), 0.0)
            # استخدام floor لتقريب للأسفل
            remaining = math.floor(max(0, original_surplus - withdrawn))
            surplus_remaining_list.append(remaining)
        
        surplus_remaining_dict[branch] = surplus_remaining_list
    
    return surplus_remaining_dict

