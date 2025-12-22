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


def _load_analytics_dataframe(analytics_path: str, has_date_header: bool) -> pd.DataFrame:
    """Load analytics DataFrame with optional header skip."""
    skiprows = 1 if has_date_header else 0
    return pd.read_csv(analytics_path, skiprows=skiprows, encoding='utf-8-sig')


def read_analytics_file(analytics_path: str) -> tuple:
    """Read an analytics file and return its data."""
    try:
        with open(analytics_path, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline().strip()
        start_date, end_date = extract_dates_from_header(first_line)
        has_date_header = bool(start_date and end_date)
        return _load_analytics_dataframe(analytics_path, has_date_header), has_date_header, first_line
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


def _update_single_row(product_totals: dict, row, branch: str, branches: list) -> None:
    """Update totals from a single row."""
    code = str(row['code'])
    if code not in product_totals:
        product_totals[code] = _initialize_product_totals(row['product_name'], branches)
    
    product_totals[code]['total_surplus'] += float(row['surplus_quantity'] or 0)
    product_totals[code]['total_needed'] += float(row['needed_quantity'] or 0)
    product_totals[code]['total_sales'] += float(row['sales'] or 0)
    product_totals[code]['branch_balances'][branch] = int(row['balance'] or 0)


def _update_product_totals(product_totals: dict, df, branch: str, branches: list) -> None:
    """Update product totals from a single branch DataFrame."""
    for _, row in df.iterrows():
        if not pd.isna(row['code']):
            _update_single_row(product_totals, row, branch, branches)


def _load_and_validate_branch_analytics(analytics_dir: str, branch: str) -> tuple:
    """Load and validate analytics file for a branch."""
    branch_dir = os.path.join(analytics_dir, branch)
    latest_file = get_latest_file(branch_dir, '.csv')
    
    if not latest_file:
        logger.warning("No analytics file found for branch: %s", branch)
        return None, False, ''
    
    analytics_path = os.path.join(branch_dir, latest_file)
    return read_analytics_file(analytics_path)


def _process_single_branch_totals(analytics_dir: str, branch: str, branches: list, 
                                   product_totals: dict, header_info: dict) -> None:
    """Process a single branch and update product totals."""
    df, branch_has_date_header, branch_first_line = _load_and_validate_branch_analytics(analytics_dir, branch)
    
    if df is None or not _has_required_columns(df, analytics_dir):
        return
    
    if not header_info['has_date_header'] and branch_has_date_header:
        header_info['has_date_header'] = True
        header_info['first_line'] = branch_first_line
    
    _update_product_totals(product_totals, df, branch, branches)


def _aggregate_branch_totals(analytics_dir: str, branches: list) -> tuple:
    """Aggregate totals across all branches."""
    product_totals = {}
    header_info = {'has_date_header': False, 'first_line': ''}
    
    for branch in branches:
        _process_single_branch_totals(analytics_dir, branch, branches, product_totals, header_info)
    
    return product_totals, header_info['has_date_header'], header_info['first_line']


def _get_shortage_columns() -> list:
    """Get ordered column list for shortage DataFrame."""
    ordered_branches = get_search_order()
    return ['code', 'product_name', 'shortage_quantity', 'total_sales'] + [f'balance_{b}' for b in ordered_branches]


def _build_shortage_row(code: str, totals: dict, branches: list) -> dict:
    """Build a single shortage row."""
    shortage_quantity = int(totals['total_needed'] - totals['total_surplus'])
    row_data = {
        'code': code,
        'product_name': totals['product_name'],
        'shortage_quantity': shortage_quantity,
        'total_sales': int(totals['total_sales'])
    }
    for branch in branches:
        row_data[f'balance_{branch}'] = totals['branch_balances'].get(branch, 0)
    return row_data


def _build_shortage_dataframe(product_totals: dict, branches: list) -> pd.DataFrame:
    """Build DataFrame from products with shortage (needed > surplus)."""
    shortage_data = [_build_shortage_row(code, totals, branches) for code, totals in product_totals.items() if totals['total_needed'] > totals['total_surplus']]
    columns = _get_shortage_columns()
    if not shortage_data:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(shortage_data).sort_values('shortage_quantity', ascending=False)[columns]


def calculate_shortage_products(analytics_dir: str) -> tuple:
    """Calculate products where total needed exceeds total surplus."""
    branches = get_branches()
    product_totals, has_date_header, first_line = _aggregate_branch_totals(analytics_dir, branches)
    shortage_df = _build_shortage_dataframe(product_totals, branches)
    return shortage_df, has_date_header, first_line


