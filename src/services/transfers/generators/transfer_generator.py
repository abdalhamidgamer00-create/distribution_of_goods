"""Generate transfer CSV files between branches"""

import os
import math
import pandas as pd

from src.core.domain.branches.config import get_branches
from src.shared.dataframes.validators import clean_numeric_series, ensure_columns
from src.shared.utils.file_handler import get_latest_file
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


# =============================================================================
# PUBLIC API
# =============================================================================

def generate_transfer_files(analytics_dir: str, transfers_dir: str, has_date_header: bool = False, first_line: str = "") -> dict:
    """Generate transfer CSV files for each source branch to all target branches."""
    return _generate_for_all_pairs(get_branches(), analytics_dir, transfers_dir, has_date_header, first_line)


def generate_transfer_for_pair(source_branch: str, target_branch: str, analytics_dir: str,
                               transfers_dir: str, has_date_header: bool = False, first_line: str = "") -> str:
    """Generate transfer CSV file from source branch to target branch."""
    analytics_path, _, base_name = _get_analytics_path(analytics_dir, target_branch)
    
    if not analytics_path:
        return None
    
    return _execute_transfer_process(analytics_path, source_branch, target_branch,
                                     transfers_dir, base_name, has_date_header, first_line)


# =============================================================================
# DATA LOADING HELPERS
# =============================================================================

def _load_analytics_file(analytics_path: str) -> pd.DataFrame:
    """Load and validate analytics file."""
    dataframe = pd.read_csv(analytics_path, encoding='utf-8-sig')
    ensure_columns(dataframe, ["code", "product_name"], context=f"analytics file {analytics_path}")
    return dataframe


def _find_analytics_file(target_analytics_dir: str) -> str:
    """Find latest analytics file in directory."""
    if not os.path.exists(target_analytics_dir):
        return None
    return get_latest_file(target_analytics_dir, '.csv')


def _get_analytics_path(analytics_dir: str, target_branch: str) -> tuple:
    """Get analytics file path and base name."""
    target_analytics_dir = os.path.join(analytics_dir, target_branch)
    latest_analytics_file = _find_analytics_file(target_analytics_dir)
    
    if not latest_analytics_file:
        return None, None, None
    
    analytics_path = os.path.join(target_analytics_dir, latest_analytics_file)
    base_name = os.path.splitext(latest_analytics_file)[0].replace(f'_{target_branch}_analytics', '')
    return analytics_path, latest_analytics_file, base_name


# =============================================================================
# TRANSFER AMOUNT CALCULATION HELPERS
# =============================================================================

def _process_transfer_column(analytics_dataframe: pd.DataFrame, source_branch: str, column_number: int) -> pd.Series:
    """Process a single transfer column pair and return amounts."""
    available_column = f'available_branch_{column_number}'
    surplus_column = f'surplus_from_branch_{column_number}'
    if available_column not in analytics_dataframe.columns or surplus_column not in analytics_dataframe.columns:
        return pd.Series(0.0, index=analytics_dataframe.index)
    available_series = analytics_dataframe[available_column].fillna("").astype(str).str.strip()
    mask = available_series.eq(source_branch)
    return clean_numeric_series(analytics_dataframe[surplus_column]).where(mask, 0.0)


def _calculate_transfer_amounts(analytics_dataframe: pd.DataFrame, source_branch: str) -> pd.Series:
    """Calculate transfer amounts from source branch columns."""
    transfer_amounts = pd.Series(0.0, index=analytics_dataframe.index)
    for column_number in range(1, 10):
        transfer_amounts += _process_transfer_column(analytics_dataframe, source_branch, column_number)
    return transfer_amounts


# =============================================================================
# DATAFRAME BUILDING HELPERS
# =============================================================================

def _build_transfer_dataframe(analytics_dataframe: pd.DataFrame, transfer_amounts: pd.Series, target_branch: str) -> pd.DataFrame:
    """Build transfer DataFrame from valid rows."""
    valid_rows = transfer_amounts > 0
    if not valid_rows.any():
        return None
    
    transfer_dataframe = analytics_dataframe.loc[valid_rows, ['code', 'product_name']].copy()
    transfer_dataframe['quantity_to_transfer'] = transfer_amounts[valid_rows].apply(lambda value: math.ceil(value)).astype(int)
    transfer_dataframe['target_branch'] = target_branch
    transfer_dataframe = transfer_dataframe.sort_values('product_name', ascending=True, key=lambda column: column.str.lower())
    return transfer_dataframe


def _build_and_validate_transfer(analytics_dataframe, source_branch: str, target_branch: str):
    """Build and validate transfer dataframe."""
    transfer_amounts = _calculate_transfer_amounts(analytics_dataframe, source_branch)
    return _build_transfer_dataframe(analytics_dataframe, transfer_amounts, target_branch)


# =============================================================================
# FILE I/O HELPERS
# =============================================================================

def _write_transfer_csv(transfer_dataframe: pd.DataFrame, transfer_path: str, 
                         has_date_header: bool, first_line: str) -> None:
    """Write transfer DataFrame to CSV file."""
    with open(transfer_path, 'w', encoding='utf-8-sig', newline='') as file_handle:
        if has_date_header:
            file_handle.write(first_line + '\n')
        transfer_dataframe.to_csv(file_handle, index=False, lineterminator='\n')


def _save_transfer_file(transfer_dataframe: pd.DataFrame, transfers_dir: str, source_branch: str,
                        target_branch: str, base_name: str, has_date_header: bool, first_line: str) -> str:
    """Save transfer DataFrame to CSV file."""
    transfer_dir = os.path.join(transfers_dir, f"transfers_from_{source_branch}_to_other_branches")
    os.makedirs(transfer_dir, exist_ok=True)
    
    transfer_file = f"{base_name}_from_{source_branch}_to_{target_branch}.csv"
    transfer_path = os.path.join(transfer_dir, transfer_file)
    
    _write_transfer_csv(transfer_dataframe, transfer_path, has_date_header, first_line)
    return transfer_path


# =============================================================================
# TRANSFER PROCESSING HELPERS
# =============================================================================

def _process_transfer(analytics_path: str, source_branch: str, target_branch: str, 
                      transfers_dir: str, base_name: str, has_date_header: bool, first_line: str) -> str:
    """Process transfer from analytics file."""
    analytics_dataframe = _load_analytics_file(analytics_path)
    transfer_dataframe = _build_and_validate_transfer(analytics_dataframe, source_branch, target_branch)
    
    if transfer_dataframe is None:
        return None
    
    return _save_transfer_file(transfer_dataframe, transfers_dir, source_branch, target_branch, base_name, has_date_header, first_line)


def _execute_transfer_process(analytics_path: str, source_branch: str, target_branch: str,
                               transfers_dir: str, base_name: str, has_date_header: bool, first_line: str) -> str:
    """Execute transfer process with error handling."""
    try:
        return _process_transfer(analytics_path, source_branch, target_branch, transfers_dir, base_name, has_date_header, first_line)
    except (ValueError, FileNotFoundError):
        return None
    except Exception as error:
        logger.exception("Warning: Error processing %s -> %s: %s", source_branch, target_branch, error)
        return None


# =============================================================================
# BATCH GENERATION HELPERS
# =============================================================================

def _collect_transfer_pairs(branches: list) -> list:
    """Collect all valid source-target pairs."""
    return [(source, target) for source in branches for target in branches if source != target]


def _generate_for_all_pairs(branches: list, analytics_dir: str, transfers_dir: str,
                             has_date_header: bool, first_line: str) -> dict:
    """Generate transfers for all branch pairs."""
    transfer_files = {}
    for source_branch, target_branch in _collect_transfer_pairs(branches):
        transfer_path = generate_transfer_for_pair(source_branch, target_branch, analytics_dir, transfers_dir, has_date_header, first_line)
        if transfer_path:
            transfer_files[(source_branch, target_branch)] = transfer_path
    return transfer_files
