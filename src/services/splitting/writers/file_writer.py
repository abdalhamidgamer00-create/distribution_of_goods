"""File writing operations"""

import os
from src.core.domain.branches.config import (
    get_analytics_columns, get_branches
)
from src.shared.utils.file_handler import ensure_directory_exists
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


# =============================================================================
# PUBLIC API
# =============================================================================

def write_branch_files(
    branches: list, 
    analytics_data: dict, 
    output_base_dir: str, 
    base_filename: str, 
    has_date_header: bool, 
    first_line: str
) -> dict:
    """Write branch files to disk."""
    results = {}
    for branch in branches:
        path = _write_single_branch(
            branch, analytics_data, output_base_dir, 
            base_filename, has_date_header, first_line
        )
        results[branch] = path
    return results


def write_analytics_files(
    branches: list, 
    analytics_data: dict, 
    analytics_dir: str, 
    base_filename: str, 
    max_withdrawals: int, 
    has_date_header: bool, 
    first_line: str
) -> None:
    """Write analytics files to disk."""
    cols = get_analytics_columns(max_withdrawals)
    for branch in branches:
        _write_single_analytics(
            branch, 
            analytics_data, 
            analytics_dir, 
            base_filename, 
            cols, 
            has_date_header, 
            first_line
        )


# =============================================================================
# CSV WRITING HELPERS
# =============================================================================

def _write_csv_with_header(
    dataframe, filepath: str, has_date_header: bool, first_line: str
) -> None:
    """Write DataFrame to CSV with optional date header."""
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as handle:
        if has_date_header:
            handle.write(first_line + '\n')
        dataframe.to_csv(handle, index=False, lineterminator='\n')
    
    if not os.path.exists(filepath):
        raise IOError(f"File was not created: {filepath}")


# =============================================================================
# BRANCH FILE HELPERS
# =============================================================================

def _write_single_branch(
    branch: str, 
    analytics_data: dict, 
    output_base_dir: str, 
    base_filename: str, 
    has_date_header: bool, 
    first_line: str
) -> str:
    """Write a single branch file and return its path."""
    branch_dataframe = analytics_data[branch]
    branch_dir = os.path.join(output_base_dir, branch)
    ensure_directory_exists(branch_dir)
    
    filename = f"{base_filename}_{branch}.csv"
    output_path = os.path.join(branch_dir, filename)
    _write_csv_with_header(
        branch_dataframe, output_path, has_date_header, first_line
    )
    logger.debug("Written branch file: %s", output_path)
    return output_path


# =============================================================================
# ANALYTICS FILE HELPERS
# =============================================================================

def _write_single_analytics(
    branch: str, 
    analytics_data: dict, 
    analytics_dir: str, 
    base_filename: str, 
    analytics_columns: list, 
    has_date_header: bool, 
    first_line: str
) -> None:
    """Write a single analytics file."""
    branch_dir = os.path.join(analytics_dir, branch)
    ensure_directory_exists(branch_dir)
    
    analytics_df = analytics_data[branch][analytics_columns].copy()
    filename = f"{base_filename}_{branch}_analytics.csv"
    analytics_path = os.path.join(branch_dir, filename)
    
    _write_csv_with_header(
        analytics_df, analytics_path, has_date_header, first_line
    )
    logger.debug("Written analytics file: %s", analytics_path)
