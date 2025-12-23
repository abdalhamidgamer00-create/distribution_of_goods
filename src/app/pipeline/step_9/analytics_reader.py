"""Analytics file reader module

Handles reading analytics files and extracting withdrawal data.
"""

import os
import pandas as pd
from src.shared.utils.file_handler import get_latest_file
from src.core.validation import extract_dates_from_header
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


# =============================================================================
# PUBLIC API
# =============================================================================

def read_analytics_file(analytics_path: str) -> tuple:
    """Read an analytics file and return its data."""
    try:
        with open(analytics_path, 'r', encoding='utf-8-sig') as file_handle:
            first_line = file_handle.readline().strip()
        
        dataframe, has_date_header = _parse_csv_with_date_header(analytics_path, first_line)
        return dataframe, has_date_header, first_line
    except Exception as error:
        logger.error("Error reading analytics file %s: %s", analytics_path, error)
        return None, False, ''


def get_latest_analytics_path(analytics_dir: str, branch: str) -> str:
    """Get the path to the latest analytics file for a branch."""
    branch_dir = os.path.join(analytics_dir, branch)
    return _build_analytics_path(branch_dir, get_latest_file(branch_dir, '.csv'))


def extract_withdrawals_from_branch(dataframe: pd.DataFrame, source_branch: str) -> dict:
    """Extract all withdrawals made FROM a specific branch."""
    withdrawal_pairs = _build_withdrawal_pairs(dataframe)
    
    all_withdrawals = {}
    for _, row in dataframe.iterrows():
        row_withdrawals = _process_withdrawal_row(row, source_branch, withdrawal_pairs)
        for code, amount in row_withdrawals.items():
            all_withdrawals[code] = all_withdrawals.get(code, 0.0) + amount
    
    return all_withdrawals


# =============================================================================
# CSV PARSING HELPERS
# =============================================================================

def _parse_csv_with_date_header(analytics_path: str, first_line: str) -> tuple:
    """Parse CSV with optional date header detection."""
    start_date, end_date = extract_dates_from_header(first_line)
    has_date_header = bool(start_date and end_date)
    
    if has_date_header:
        dataframe = pd.read_csv(analytics_path, skiprows=1, encoding='utf-8-sig')
    else:
        dataframe = pd.read_csv(analytics_path, encoding='utf-8-sig')
    
    return dataframe, has_date_header


# =============================================================================
# PATH BUILDING HELPERS
# =============================================================================

def _build_analytics_path(branch_dir: str, latest_file: str) -> str:
    """Build full path to analytics file."""
    return os.path.join(branch_dir, latest_file) if latest_file else None


# =============================================================================
# WITHDRAWAL EXTRACTION HELPERS
# =============================================================================

def _build_withdrawal_pairs(dataframe: pd.DataFrame) -> list:
    """Build withdrawal column pairs."""
    surplus_from_columns = [column for column in dataframe.columns if column.startswith('surplus_from_branch_')]
    available_branch_columns = [column for column in dataframe.columns if column.startswith('available_branch_')]
    min_columns = min(len(surplus_from_columns), len(available_branch_columns))
    return list(zip(available_branch_columns[:min_columns], surplus_from_columns[:min_columns]))


def _extract_withdrawal_amount(row, available_column: str, surplus_column: str, source_branch: str) -> float:
    """Extract withdrawal amount from a single column pair."""
    if pd.notna(row.get(available_column)) and str(row[available_column]).strip() == source_branch:
        if pd.notna(row.get(surplus_column)):
            try:
                return float(row[surplus_column])
            except (ValueError, TypeError):
                pass
    return 0.0


def _process_withdrawal_row(row, source_branch: str, withdrawal_pairs: list) -> dict:
    """Process a single row and extract withdrawals from source branch."""
    product_code = row.get('code')
    if pd.isna(product_code):
        return {}
    
    product_code = str(product_code)
    total = sum(_extract_withdrawal_amount(row, available, surplus, source_branch) for available, surplus in withdrawal_pairs)
    return {product_code: total} if total > 0 else {}
