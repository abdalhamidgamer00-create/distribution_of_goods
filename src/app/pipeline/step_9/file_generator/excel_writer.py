"""Excel writer logic."""

import os
import pandas as pd
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def generate_excel_files(files_info: dict, branch: str, output_dir: str) -> int:
    """Convert CSV files to Excel format."""
    branch_dir = os.path.join(output_dir, branch)
    os.makedirs(branch_dir, exist_ok=True)
    success_count = 0
    for category, file_info in files_info.items():
        base_csv = os.path.basename(file_info['csv_path'])
        excel_filename = os.path.splitext(base_csv)[0] + '.xlsx'
        target_path = os.path.join(branch_dir, excel_filename)
        
        if _convert_single_to_excel(
            file_info, target_path, branch, category
        ):
            success_count += 1
    return success_count


def _convert_single_to_excel(
    file_info: dict, 
    excel_path: str, 
    branch: str, 
    category: str
) -> bool:
    """Convert a single CSV file info to Excel."""
    try:
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            file_info['df'].to_excel(
                writer, index=False, sheet_name='Remaining Surplus'
            )
        return True
    except Exception as error:
        logger.error(
            "Error creating Excel file for %s/%s: %s", 
            branch, category, error
        )
        return False
