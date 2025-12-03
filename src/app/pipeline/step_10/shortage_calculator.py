"""Shortage calculator module

Calculates products where total needed quantity exceeds total surplus.
"""

import os
import pandas as pd
from src.core.domain.branches.config import get_branches, get_search_order
from src.shared.utils.file_handler import get_latest_file
from src.core.validation.data_validator import extract_dates_from_header
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def read_analytics_file(analytics_path: str) -> tuple:
    """
    Read an analytics file and return its data.
    
    Args:
        analytics_path: Path to the analytics CSV file
        
    Returns:
        Tuple of (DataFrame, has_date_header, first_line)
    """
    try:
        with open(analytics_path, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline().strip()
        
        start_date, end_date = extract_dates_from_header(first_line)
        has_date_header = bool(start_date and end_date)
        
        if has_date_header:
            df = pd.read_csv(analytics_path, skiprows=1, encoding='utf-8-sig')
        else:
            df = pd.read_csv(analytics_path, encoding='utf-8-sig')
        
        return df, has_date_header, first_line
        
    except Exception as e:
        logger.error("Error reading analytics file %s: %s", analytics_path, e)
        return None, False, ''


def calculate_shortage_products(analytics_dir: str) -> tuple:
    """
    Calculate products where total needed exceeds total surplus.
    
    For each product:
    - Sum surplus_quantity across all branches = total_surplus
    - Sum needed_quantity across all branches = total_needed
    - If total_needed > total_surplus: shortage = total_needed - total_surplus
    - Also includes balance for each branch
    
    Args:
        analytics_dir: Base analytics directory
        
    Returns:
        Tuple of (DataFrame with shortage products, has_date_header, first_line)
    """
    branches = get_branches()
    
    # Dictionary to store totals per product
    # Key: product_code, Value: {product_name, total_surplus, total_needed, balance_per_branch}
    product_totals = {}
    
    has_date_header = False
    first_line = ''
    
    for branch in branches:
        branch_dir = os.path.join(analytics_dir, branch)
        latest_file = get_latest_file(branch_dir, '.csv')
        
        if not latest_file:
            logger.warning("No analytics file found for branch: %s", branch)
            continue
        
        analytics_path = os.path.join(branch_dir, latest_file)
        df, branch_has_date_header, branch_first_line = read_analytics_file(analytics_path)
        
        if df is None:
            continue
        
        # Store date header info from first successful read
        if not has_date_header and branch_has_date_header:
            has_date_header = True
            first_line = branch_first_line
        
        # Check required columns
        required_cols = ['code', 'product_name', 'surplus_quantity', 'needed_quantity', 'balance', 'sales']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.warning("Missing columns in %s: %s", analytics_path, missing_cols)
            continue
        
        # Aggregate totals for each product
        for _, row in df.iterrows():
            code = row['code']
            if pd.isna(code):
                continue
            
            code = str(code)
            product_name = row['product_name']
            surplus = float(row['surplus_quantity']) if pd.notna(row['surplus_quantity']) else 0.0
            needed = float(row['needed_quantity']) if pd.notna(row['needed_quantity']) else 0.0
            balance = int(row['balance']) if pd.notna(row['balance']) else 0
            sales = float(row['sales']) if pd.notna(row['sales']) else 0.0
            
            if code not in product_totals:
                product_totals[code] = {
                    'product_name': product_name,
                    'total_surplus': 0.0,
                    'total_needed': 0.0,
                    'total_sales': 0.0,
                    'branch_balances': {b: 0 for b in branches}
                }
            
            product_totals[code]['total_surplus'] += surplus
            product_totals[code]['total_needed'] += needed
            product_totals[code]['total_sales'] += sales
            product_totals[code]['branch_balances'][branch] = balance
    
    # Calculate shortage (where needed > surplus)
    shortage_data = []
    for code, totals in product_totals.items():
        total_surplus = totals['total_surplus']
        total_needed = totals['total_needed']
        
        # Shortage = total_needed - total_surplus (only if negative balance)
        if total_needed > total_surplus:
            shortage_quantity = int(total_needed - total_surplus)
            row_data = {
                'code': code,
                'product_name': totals['product_name'],
                'shortage_quantity': shortage_quantity,
                'total_sales': int(totals['total_sales'])
            }
            
            # Add balance for each branch
            for branch in branches:
                row_data[f'balance_{branch}'] = totals['branch_balances'].get(branch, 0)
            
            shortage_data.append(row_data)
    
    if not shortage_data:
        # Create empty DataFrame with all columns including branch balances
        ordered_branches = get_search_order()
        columns = ['code', 'product_name', 'shortage_quantity', 'total_sales'] + [f'balance_{b}' for b in ordered_branches]
        return pd.DataFrame(columns=columns), has_date_header, first_line
    
    # Create DataFrame and sort by shortage_quantity (descending)
    result_df = pd.DataFrame(shortage_data)
    result_df = result_df.sort_values(
        'shortage_quantity',
        ascending=False
    )
    
    # Reorder columns: code, product_name, shortage_quantity, total_sales, then branch balances (in search order)
    ordered_branches = get_search_order()
    column_order = ['code', 'product_name', 'shortage_quantity', 'total_sales'] + [f'balance_{b}' for b in ordered_branches]
    result_df = result_df[column_order]
    
    return result_df, has_date_header, first_line

