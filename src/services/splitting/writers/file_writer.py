"""File writing operations"""

import os
from src.core.domain.branches.config import get_analytics_columns, get_branches
from src.shared.utils.file_handler import ensure_directory_exists
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def write_branch_files(
    branches: list, 
    analytics_data: dict, 
    output_base_dir: str, 
    base_filename: str, 
    has_date_header: bool, 
    first_line: str
) -> dict:
    """
    Write branch files to disk
    
    Args:
        branches: List of branch names
        analytics_data: Dictionary mapping branch to branch_df
        output_base_dir: Base directory for output files
        base_filename: Base filename (without extension)
        has_date_header: Whether to include date header
        first_line: First line (date header) to write if has_date_header is True
        
    Returns:
        Dictionary with branch names as keys and output file paths as values
    """
    output_files = {}
    
    for branch in branches:
        branch_df = analytics_data[branch]
        branch_dir = os.path.join(output_base_dir, branch)
        ensure_directory_exists(branch_dir)
        
        output_file = f"{base_filename}_{branch}.csv"
        output_path = os.path.join(branch_dir, output_file)
        
        try:
            with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
                if has_date_header:
                    f.write(first_line + '\n')
                branch_df.to_csv(f, index=False, lineterminator='\n')
            
            # التحقق من نجاح الكتابة
            if not os.path.exists(output_path):
                raise IOError(f"File was not created: {output_path}")
            
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
    """
    Write analytics files to disk
    
    Args:
        branches: List of branch names
        analytics_data: Dictionary mapping branch to branch_df
        analytics_dir: Directory for analytics files
        base_filename: Base filename (without extension)
        max_withdrawals: Maximum number of withdrawal columns
        has_date_header: Whether to include date header
        first_line: First line (date header) to write if has_date_header is True
    """
    analytics_columns = get_analytics_columns(max_withdrawals)
    
    for branch in branches:
        branch_dir = os.path.join(analytics_dir, branch)
        ensure_directory_exists(branch_dir)
        
        analytics_df = analytics_data[branch][analytics_columns].copy()
        analytics_file = f"{base_filename}_{branch}_analytics.csv"
        analytics_path = os.path.join(branch_dir, analytics_file)
        
        try:
            with open(analytics_path, 'w', encoding='utf-8-sig', newline='') as f:
                if has_date_header:
                    f.write(first_line + '\n')
                analytics_df.to_csv(f, index=False, lineterminator='\n')
            
            # التحقق من نجاح الكتابة
            if not os.path.exists(analytics_path):
                raise IOError(f"Analytics file was not created: {analytics_path}")
            
            logger.debug("Written analytics file: %s", analytics_path)
            
        except Exception as e:
            logger.error("Failed to write analytics file for %s: %s", branch, e)
            raise

