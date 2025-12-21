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

REQUIRED_COLUMNS = ['code', 'product_name', 'surplus_quantity', 'needed_quantity', 'balance', 'sales']


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


def _has_required_columns(df: pd.DataFrame, analytics_path: str) -> bool:
    """Check if DataFrame has all required columns."""
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        logger.warning("Missing columns in %s: %s", analytics_path, missing_cols)
        return False
    return True


def _initialize_product_totals(product_name: str, branches: list) -> dict:
    """Create initial product totals dictionary."""
    return {
        'product_name': product_name,
        'total_surplus': 0.0,
        'total_needed': 0.0,
        'total_sales': 0.0,
        'branch_balances': {b: 0 for b in branches}
    }


def _aggregate_branch_totals(analytics_dir: str, branches: list) -> tuple:
    """
    Aggregate totals across all branches.
    
    Returns:
        Tuple of (product_totals dict, has_date_header, first_line)
    """
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
        
        if not has_date_header and branch_has_date_header:
            has_date_header = True
            first_line = branch_first_line
        
        if not _has_required_columns(df, analytics_path):
            continue
        
        for _, row in df.iterrows():
            code = row['code']
            if pd.isna(code):
                continue
            
            code = str(code)
            if code not in product_totals:
                product_totals[code] = _initialize_product_totals(row['product_name'], branches)
            
            product_totals[code]['total_surplus'] += float(row['surplus_quantity'] or 0)
            product_totals[code]['total_needed'] += float(row['needed_quantity'] or 0)
            product_totals[code]['total_sales'] += float(row['sales'] or 0)
            product_totals[code]['branch_balances'][branch] = int(row['balance'] or 0)
    
    return product_totals, has_date_header, first_line


def _build_shortage_dataframe(product_totals: dict, branches: list) -> pd.DataFrame:
    """Build DataFrame from products with shortage (needed > surplus)."""
    shortage_data = []
    
    for code, totals in product_totals.items():
        if totals['total_needed'] <= totals['total_surplus']:
            continue
        
        shortage_quantity = int(totals['total_needed'] - totals['total_surplus'])
        row_data = {
            'code': code,
            'product_name': totals['product_name'],
            'shortage_quantity': shortage_quantity,
            'total_sales': int(totals['total_sales'])
        }
        
        for branch in branches:
            row_data[f'balance_{branch}'] = totals['branch_balances'].get(branch, 0)
        
        shortage_data.append(row_data)
    
    if not shortage_data:
        ordered_branches = get_search_order()
        columns = ['code', 'product_name', 'shortage_quantity', 'total_sales'] + [f'balance_{b}' for b in ordered_branches]
        return pd.DataFrame(columns=columns)
    
    result_df = pd.DataFrame(shortage_data)
    result_df = result_df.sort_values('shortage_quantity', ascending=False)
    
    ordered_branches = get_search_order()
    column_order = ['code', 'product_name', 'shortage_quantity', 'total_sales'] + [f'balance_{b}' for b in ordered_branches]
    return result_df[column_order]


def calculate_shortage_products(analytics_dir: str) -> tuple:
    """
    Calculate products where total needed exceeds total surplus.
    
    Args:
        analytics_dir: Base analytics directory
        
    Returns:
        Tuple of (DataFrame with shortage products, has_date_header, first_line)
    """
    branches = get_branches()
    product_totals, has_date_header, first_line = _aggregate_branch_totals(analytics_dir, branches)
    shortage_df = _build_shortage_dataframe(product_totals, branches)
    
    return shortage_df, has_date_header, first_line


