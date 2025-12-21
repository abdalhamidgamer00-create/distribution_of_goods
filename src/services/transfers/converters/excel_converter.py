"""Convert split CSV files to Excel format"""

import os
import pandas as pd

from src.core.domain.classification.product_classifier import get_product_categories
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _build_excel_output_path(csv_file_path: str, excel_output_dir: str) -> str:
    """Build output path for Excel file maintaining folder structure."""
    csv_dir = os.path.dirname(csv_file_path)
    csv_filename = os.path.basename(csv_file_path)
    
    subfolder_name = os.path.basename(csv_dir)
    parent_dir_path = os.path.dirname(csv_dir)
    parent_dir = os.path.basename(parent_dir_path)
    
    excel_parent_dir = parent_dir.replace('transfers', 'transfers_excel')
    excel_subfolder = os.path.join(excel_output_dir, excel_parent_dir, subfolder_name)
    os.makedirs(excel_subfolder, exist_ok=True)
    
    excel_filename = os.path.splitext(csv_filename)[0] + '.xlsx'
    return os.path.join(excel_subfolder, excel_filename)


def convert_split_csv_to_excel(csv_file_path: str, excel_output_dir: str, has_date_header: bool = False, first_line: str = "") -> str:
    """Convert a split CSV file to Excel format."""
    try:
        df = pd.read_csv(csv_file_path, encoding='utf-8-sig')
        excel_path = _build_excel_output_path(csv_file_path, excel_output_dir)
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        return excel_path
    
    except Exception as e:
        logger.exception("Error converting %s to Excel: %s", csv_file_path, e)
        return None


def convert_all_split_files_to_excel(transfers_base_dir: str, excel_output_dir: str, has_date_header: bool = False, first_line: str = "") -> int:
    """
    Convert all split CSV files to Excel format
    
    Args:
        transfers_base_dir: Base directory containing split CSV files
        excel_output_dir: Base directory for Excel output files
        has_date_header: Whether CSV files have date headers
        first_line: First line (date header) if has_date_header is True
        
    Returns:
        Number of Excel files successfully created
    """
    count = 0
    categories = get_product_categories()
    
    for root, dirs, files in os.walk(transfers_base_dir):
        for file in files:
            if file.endswith('.csv'):
                # Only process split category files (files ending with category name)
                is_split_file = any(file.endswith(f'_{cat}.csv') for cat in categories)
                if is_split_file:
                    csv_file_path = os.path.join(root, file)
                    excel_path = convert_split_csv_to_excel(csv_file_path, excel_output_dir, has_date_header, first_line)
                    if excel_path:
                        count += 1
    
    return count

