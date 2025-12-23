"""Matrix building helpers."""

import pandas as pd


def build_branch_matrices(branch_data: dict, branches: list) -> dict:
    """Build DataFrames for each metric from branch data."""
    return {
        'avg_sales': pd.DataFrame({
            branch: branch_data[branch]['avg_sales'].astype(float) 
            for branch in branches
        }),
        'balance': pd.DataFrame({
            branch: branch_data[branch]['balance'].astype(float) 
            for branch in branches
        }),
        'needed': pd.DataFrame({
            branch: branch_data[branch]['needed_quantity'].astype(float) 
            for branch in branches
        }),
        'surplus': pd.DataFrame({
            branch: branch_data[branch]['surplus_quantity'].astype(float) 
            for branch in branches
        }),
    }


def setup_allocation_data(branch_data: dict, branches: list) -> tuple:
    """Setup matrices and calculate totals for allocation."""
    matrices = build_branch_matrices(branch_data, branches)
    total_needed = matrices['needed'].clip(lower=0).sum(axis=1)
    total_surplus = matrices['surplus'].clip(lower=0).sum(axis=1)
    needs_mask = (total_needed > 0) & (total_surplus > 0) & (
        total_surplus < total_needed
    )
    return matrices, total_needed, total_surplus, needs_mask
