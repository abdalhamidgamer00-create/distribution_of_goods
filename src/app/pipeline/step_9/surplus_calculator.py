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


def calculate_total_withdrawals(analytics_dir: str, branch: str) -> dict:
    """
    Calculate total withdrawals FROM a specific branch across all analytics files.
    
    Reads all branch analytics files and sums up withdrawals
    that were taken from the specified branch.
    
    Args:
        analytics_dir: Base analytics directory
        branch: The source branch to calculate withdrawals from
        
    Returns:
        Dictionary mapping product_code -> total_withdrawn_quantity
    """
    total_withdrawals = {}
    branches = get_branches()
    
    for other_branch in branches:
        analytics_path = get_latest_analytics_path(analytics_dir, other_branch)
        if not analytics_path:
            continue
        
        df, _, _ = read_analytics_file(analytics_path)
        if df is None:
            continue
        
        # Extract withdrawals from our branch
        branch_withdrawals = extract_withdrawals_from_branch(df, branch)
        
        # Accumulate totals
        for product_code, amount in branch_withdrawals.items():
            total_withdrawals[product_code] = total_withdrawals.get(product_code, 0.0) + amount
    
    return total_withdrawals


def calculate_remaining_surplus(df: pd.DataFrame, total_withdrawals: dict) -> pd.DataFrame:
    """
    Calculate remaining surplus for each product.
    
    Subtracts total withdrawals from original surplus quantity.
    
    Args:
        df: DataFrame with 'code' and 'surplus_quantity' columns
        total_withdrawals: Dictionary of product_code -> total_withdrawn
        
    Returns:
        DataFrame with products that have remaining surplus > 0,
        containing columns: code, product_name, surplus_remaining
    """
    # Map withdrawals to products
    df = df.copy()
    df['total_withdrawn'] = df['code'].astype(str).map(total_withdrawals).fillna(0.0)
    df['calculated_remaining'] = df['surplus_quantity'] - df['total_withdrawn']
    
    # Filter products with remaining surplus
    remaining_df = df[df['calculated_remaining'] > 0].copy()
    
    if remaining_df.empty:
        return pd.DataFrame(columns=['code', 'product_name', 'surplus_remaining'])
    
    # Create result DataFrame
    result_df = pd.DataFrame({
        'code': remaining_df['code'],
        'product_name': remaining_df['product_name'],
        'surplus_remaining': remaining_df['calculated_remaining'].astype(int)
    })
    
    # Sort by product name (case-insensitive)
    result_df = result_df.sort_values(
        'product_name', 
        ascending=True,
        key=lambda x: x.str.lower()
    )
    
    return result_df


def validate_analytics_columns(df: pd.DataFrame) -> list:
    """
    Validate that required columns exist in the DataFrame.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        List of missing column names (empty if all present)
    """
    required_columns = ['code', 'product_name', 'surplus_quantity']
    return [col for col in required_columns if col not in df.columns]

