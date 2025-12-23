"""Core aggregation logic for shortage calculation."""

import pandas as pd
from src.app.pipeline.step_10.shortage_calculator import (
    loading,
    validation,
)


def initialize_product_totals(product_name: str, branches: list) -> dict:
    """Create initial product totals dictionary."""
    return {
        'product_name': product_name,
        'total_surplus': 0.0,
        'total_needed': 0.0,
        'total_sales': 0.0,
        'branch_balances': {branch: 0 for branch in branches}
    }


def update_single_row(
    product_totals: dict, 
    row, 
    branch: str, 
    branches: list
) -> None:
    """Update totals from a single row."""
    code = str(row['code'])
    if code not in product_totals:
        product_totals[code] = initialize_product_totals(
            row['product_name'], branches
        )
    
    product_totals[code]['total_surplus'] += float(
        row['surplus_quantity'] or 0
    )
    product_totals[code]['total_needed'] += float(
        row['needed_quantity'] or 0
    )
    product_totals[code]['total_sales'] += float(row['sales'] or 0)
    product_totals[code]['branch_balances'][branch] = int(row['balance'] or 0)


def update_product_totals(
    product_totals: dict, 
    dataframe, 
    branch: str, 
    branches: list
) -> None:
    """Update product totals from a single branch DataFrame."""
    for _, row in dataframe.iterrows():
        if not pd.isna(row['code']):
            update_single_row(product_totals, row, branch, branches)


def process_single_branch_totals(
    analytics_dir: str, 
    branch: str, 
    branches: list, 
    product_totals: dict, 
    header_info: dict
) -> None:
    """Process a single branch and update product totals."""
    result = loading.load_and_validate_branch_analytics(analytics_dir, branch)
    dataframe, branch_has_date_header, branch_first_line = result
    
    if (dataframe is None or 
            not validation.has_required_columns(dataframe, analytics_dir)):
        return
        
    if not header_info['has_date_header'] and branch_has_date_header:
        header_info['has_date_header'] = True
        header_info['first_line'] = branch_first_line
        
    update_product_totals(product_totals, dataframe, branch, branches)


def aggregate_branch_totals(analytics_dir: str, branches: list) -> tuple:
    """Aggregate totals across all branches."""
    product_totals = {}
    header_info = {'has_date_header': False, 'first_line': ''}
    
    for branch in branches:
        process_single_branch_totals(
            analytics_dir, branch, branches, product_totals, header_info
        )
    
    return (
        product_totals, 
        header_info['has_date_header'], 
        header_info['first_line']
    )
