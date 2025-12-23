"""Convert split CSV files to Excel format"""

import os
import pandas as pd

from src.core.domain.classification.product_classifier import (
    get_product_categories
)
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


# =============================================================================
# PUBLIC API
# =============================================================================

def convert_split_csv_to_excel(
    csv_file_path: str, excel_output_dir: str, 
    has_date_header: bool = False, first_line: str = ""
) -> str:
    """Convert a split CSV file to Excel format."""
    try:
        dataframe = pd.read_csv(csv_file_path, encoding='utf-8-sig')
        output_path = _build_excel_output_path(csv_file_path, excel_output_dir)
        return _write_excel_file(dataframe, output_path)
    except Exception as error:
        logger.exception(
            "Error converting %s to Excel: %s", csv_file_path, error
        )
        return None


def convert_all_split_files_to_excel(
    transfers_base_dir: str, excel_output_dir: str, 
    has_date_header: bool = False, first_line: str = ""
) -> int:
    """Convert all split CSV files to Excel format."""
    return _process_split_files(
        transfers_base_dir, 
        excel_output_dir, 
        has_date_header, 
        first_line, 
        get_product_categories()
    )


# =============================================================================
# PATH BUILDING HELPERS
# =============================================================================

def _get_excel_subfolder(csv_dir: str, excel_output_dir: str) -> str:
    """Get and create Excel subfolder path."""
    subfolder_name = os.path.basename(csv_dir)
    parent_dir = os.path.basename(os.path.dirname(csv_dir))
    excel_parent_dir = parent_dir.replace('transfers', 'transfers_excel')
    excel_subfolder = os.path.join(
        excel_output_dir, excel_parent_dir, subfolder_name
    )
    os.makedirs(excel_subfolder, exist_ok=True)
    return excel_subfolder


def _build_excel_output_path(csv_file_path: str, excel_output_dir: str) -> str:
    """Build output path for Excel file maintaining folder structure."""
    csv_dir = os.path.dirname(csv_file_path)
    excel_subfolder = _get_excel_subfolder(csv_dir, excel_output_dir)
    filename_base = os.path.splitext(os.path.basename(csv_file_path))[0]
    excel_filename = filename_base + '.xlsx'
    return os.path.join(excel_subfolder, excel_filename)


# =============================================================================
# FILE WRITING HELPERS
# =============================================================================

def _write_excel_file(dataframe, excel_path: str) -> str:
    """Write DataFrame to Excel file."""
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        dataframe.to_excel(writer, index=False, sheet_name='Sheet1')
    return excel_path


# =============================================================================
# BATCH PROCESSING HELPERS
# =============================================================================

def _is_category_file(filename: str, categories: list) -> bool:
    """Check if file is a split category file."""
    if not filename.endswith('.csv'):
        return False
        
    return any(
        filename.endswith(f'_{category}.csv') for category in categories
    )


def _process_split_files(
    transfers_base_dir: str, 
    excel_output_dir: str, 
    has_date_header: bool, 
    first_line: str, 
    categories: list
) -> int:
    """Process all split CSV files and convert to Excel."""
    count = 0
    for root, _, files in os.walk(transfers_base_dir):
        for filename in files:
            if _is_category_file(filename, categories):
                path = os.path.join(root, filename)
                excel_path = convert_split_csv_to_excel(
                    path, excel_output_dir, has_date_header, first_line
                )
                if excel_path:
                    count += 1
    return count
