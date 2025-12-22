"""Analytics file reader module

Handles reading analytics files and extracting withdrawal data.
"""

import os
import pandas as pd
from src.shared.utils.file_handler import get_latest_file
from src.core.validation.data_validator import extract_dates_from_header
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _parse_csv_with_date_header(analytics_path: str, first_line: str) -> tuple:
    """Parse CSV with optional date header detection."""
    start_date, end_date = extract_dates_from_header(first_line)
    has_date_header = bool(start_date and end_date)
    
    if has_date_header:
        df = pd.read_csv(analytics_path, skiprows=1, encoding='utf-8-sig')
    else:
        df = pd.read_csv(analytics_path, encoding='utf-8-sig')
    
    return df, has_date_header


def read_analytics_file(analytics_path: str) -> tuple:
    """Read an analytics file and return its data."""
    try:
        with open(analytics_path, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline().strip()
        
        df, has_date_header = _parse_csv_with_date_header(analytics_path, first_line)
        return df, has_date_header, first_line
    except Exception as e:
        logger.error("Error reading analytics file %s: %s", analytics_path, e)
        return None, False, ''


def get_latest_analytics_path(analytics_dir: str, branch: str) -> str:
    """
    Get the path to the latest analytics file for a branch.
    
    Args:
        analytics_dir: Base analytics directory
        branch: Branch name
        
    Returns:
        Full path to the latest analytics file, or None if not found
    """
    branch_dir = os.path.join(analytics_dir, branch)
    latest_file = get_latest_file(branch_dir, '.csv')
    
    if not latest_file:
        return None
    
    return os.path.join(branch_dir, latest_file)


def _process_withdrawal_row(row, source_branch: str, withdrawal_pairs: list) -> dict:
    """Process a single row and extract withdrawals from source branch."""
    withdrawals = {}
    product_code = row.get('code')
    
    if pd.isna(product_code):
        return withdrawals
    
    product_code = str(product_code)
    
    for available_col, surplus_col in withdrawal_pairs:
        if pd.notna(row.get(available_col)) and str(row[available_col]).strip() == source_branch:
            if pd.notna(row.get(surplus_col)):
                try:
                    amount = float(row[surplus_col])
                    withdrawals[product_code] = withdrawals.get(product_code, 0.0) + amount
                except (ValueError, TypeError):
                    pass
    
    return withdrawals


def extract_withdrawals_from_branch(df: pd.DataFrame, source_branch: str) -> dict:
    """Extract all withdrawals made FROM a specific branch."""
    surplus_from_cols = [col for col in df.columns if col.startswith('surplus_from_branch_')]
    available_branch_cols = [col for col in df.columns if col.startswith('available_branch_')]
    
    min_cols = min(len(surplus_from_cols), len(available_branch_cols))
    withdrawal_pairs = list(zip(available_branch_cols[:min_cols], surplus_from_cols[:min_cols]))
    
    all_withdrawals = {}
    for _, row in df.iterrows():
        row_withdrawals = _process_withdrawal_row(row, source_branch, withdrawal_pairs)
        for code, amount in row_withdrawals.items():
            all_withdrawals[code] = all_withdrawals.get(code, 0.0) + amount
    
    return all_withdrawals

