"""Generate transfer CSV files between branches"""

import os
import math
import pandas as pd

from src.core.domain.branches.config import get_branches
from src.shared.dataframes.validators import clean_numeric_series, ensure_columns
from src.shared.utils.file_handler import get_latest_file
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def generate_transfer_for_pair(source_branch: str, target_branch: str, analytics_dir: str, transfers_dir: str, has_date_header: bool = False, first_line: str = "") -> str:
    """
    Generate transfer CSV file from source branch to target branch
    
    Args:
        source_branch: Source branch name (e.g., 'wardani')
        target_branch: Target branch name (e.g., 'admin')
        analytics_dir: Directory containing analytics CSV files
        transfers_dir: Directory to save transfer files
        has_date_header: Whether to include date header in output files
        first_line: First line (date header) to write if has_date_header is True
        
    Returns:
        Output file path if successful, None otherwise
    """
    target_analytics_dir = os.path.join(analytics_dir, target_branch)
    
    if not os.path.exists(target_analytics_dir):
        return None
    
    latest_analytics_file = get_latest_file(target_analytics_dir, '.csv')
    if not latest_analytics_file:
        return None
    
    analytics_path = os.path.join(target_analytics_dir, latest_analytics_file)
    
    try:
        analytics_df = pd.read_csv(analytics_path, encoding='utf-8-sig')
        try:
            ensure_columns(
                analytics_df,
                ["code", "product_name"],
                context=f"analytics file {analytics_path}",
            )
        except ValueError as exc:
            logger.error("%s", exc)
            return None
        
        base_name = os.path.splitext(latest_analytics_file)[0]
        base_name = base_name.replace(f'_{target_branch}_analytics', '')
        
        transfer_amounts = pd.Series(0.0, index=analytics_df.index)
        for col_num in range(1, 10):
            available_col = f'available_branch_{col_num}'
            surplus_col = f'surplus_from_branch_{col_num}'
            
            if available_col in analytics_df.columns and surplus_col in analytics_df.columns:
                available_series = (
                    analytics_df[available_col]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )
                mask = available_series.eq(source_branch)
                surplus_series = clean_numeric_series(analytics_df[surplus_col])
                transfer_amounts += surplus_series.where(mask, 0.0)
        
        valid_rows = transfer_amounts > 0
        if not valid_rows.any():
            return None
        
        transfer_df = analytics_df.loc[valid_rows, ['code', 'product_name']].copy()
        # استخدام ceil لتقريب للأعلى ثم تحويل إلى int
        transfer_df['quantity_to_transfer'] = transfer_amounts[valid_rows].apply(lambda x: math.ceil(x)).astype(int)
        transfer_df['target_branch'] = target_branch
        transfer_df = transfer_df.sort_values(
            'product_name', 
            ascending=True,
            key=lambda x: x.str.lower()
        )
        
        transfer_dir = os.path.join(
            transfers_dir, f"transfers_from_{source_branch}_to_other_branches"
        )
        os.makedirs(transfer_dir, exist_ok=True)
        
        transfer_file = f"{base_name}_from_{source_branch}_to_{target_branch}.csv"
        transfer_path = os.path.join(transfer_dir, transfer_file)
        
        with open(transfer_path, 'w', encoding='utf-8-sig', newline='') as f:
            if has_date_header:
                f.write(first_line + '\n')
            transfer_df.to_csv(f, index=False, lineterminator='\n')
        
        return transfer_path
    
    except FileNotFoundError:
        return None
    except Exception as e:
        logger.exception("Warning: Error processing %s -> %s: %s", source_branch, target_branch, e)
        return None


def generate_transfer_files(analytics_dir: str, transfers_dir: str, has_date_header: bool = False, first_line: str = "") -> dict:
    """
    Generate transfer CSV files for each source branch to all target branches
    Uses the latest analytics file for each target branch
    
    Args:
        analytics_dir: Directory containing analytics CSV files
        transfers_dir: Directory to save transfer files
        has_date_header: Whether to include date header in output files
        first_line: First line (date header) to write if has_date_header is True
        
    Returns:
        Dictionary mapping (source_branch, target_branch) to output file path
    """
    branches = get_branches()
    transfer_files = {}
    
    for source_branch in branches:
        for target_branch in branches:
            if source_branch == target_branch:
                continue
            
            transfer_path = generate_transfer_for_pair(
                source_branch, target_branch, analytics_dir, transfers_dir,
                has_date_header, first_line
            )
            
            if transfer_path:
                transfer_files[(source_branch, target_branch)] = transfer_path
    
    return transfer_files

