"""File writing operations"""

import os
from src.core.domain.branches.config import get_analytics_columns, get_branches
from src.shared.utils.file_handler import ensure_directory_exists
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _write_csv_with_header(df, filepath: str, has_date_header: bool, first_line: str) -> None:
    """Write DataFrame to CSV with optional date header."""
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
        if has_date_header:
            f.write(first_line + '\n')
        df.to_csv(f, index=False, lineterminator='\n')
    
    if not os.path.exists(filepath):
        raise IOError(f"File was not created: {filepath}")


def write_branch_files(
    branches: list, 
    analytics_data: dict, 
    output_base_dir: str, 
    base_filename: str, 
    has_date_header: bool, 
    first_line: str
) -> dict:
    """Write branch files to disk."""
    output_files = {}
    
    for branch in branches:
        branch_df = analytics_data[branch]
        branch_dir = os.path.join(output_base_dir, branch)
        ensure_directory_exists(branch_dir)
        
        output_file = f"{base_filename}_{branch}.csv"
        output_path = os.path.join(branch_dir, output_file)
        
        try:
            _write_csv_with_header(branch_df, output_path, has_date_header, first_line)
            output_files[branch] = output_path
            logger.debug("Written branch file: %s", output_path)
        except Exception as e:
            logger.error("Failed to write branch file for %s: %s", branch, e)
            raise
    
    return output_files


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
    analytics_columns = get_analytics_columns(max_withdrawals)
    
    for branch in branches:
        branch_dir = os.path.join(analytics_dir, branch)
        ensure_directory_exists(branch_dir)
        
        analytics_df = analytics_data[branch][analytics_columns].copy()
        analytics_file = f"{base_filename}_{branch}_analytics.csv"
        analytics_path = os.path.join(branch_dir, analytics_file)
        
        try:
            _write_csv_with_header(analytics_df, analytics_path, has_date_header, first_line)
            logger.debug("Written analytics file: %s", analytics_path)
        except Exception as e:
            logger.error("Failed to write analytics file for %s: %s", branch, e)
            raise


