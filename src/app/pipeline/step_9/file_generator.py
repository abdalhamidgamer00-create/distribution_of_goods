"""File generator module

Generates CSV and Excel output files for remaining surplus.
"""

import os
from datetime import datetime
import pandas as pd
from src.core.domain.classification.product_classifier import (
    classify_product_type,
    get_product_categories,
)
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


# =============================================================================
# PUBLIC API
# =============================================================================

def add_product_type_column(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Add product_type column based on product_name."""
    dataframe = dataframe.copy()
    dataframe['product_type'] = dataframe['product_name'].apply(classify_product_type)
    return dataframe


def generate_csv_files(dataframe: pd.DataFrame, branch: str, output_dir: str, base_name: str,
                       timestamp: str, has_date_header: bool = False, first_line: str = '') -> dict:
    """Generate CSV files split by product category."""
    branch_dir = os.path.join(output_dir, branch)
    os.makedirs(branch_dir, exist_ok=True)
    generated_files = {}
    for category in get_product_categories():
        category_dataframe = _process_category_dataframe(dataframe, category)
        if category_dataframe is not None:
            generated_files[category] = _save_category_file(
                category_dataframe, branch_dir, base_name, branch, 
                timestamp, category, has_date_header, first_line
            )
    return generated_files


def generate_excel_files(files_info: dict, branch: str, output_dir: str) -> int:
    """Convert CSV files to Excel format."""
    branch_dir = os.path.join(output_dir, branch)
    os.makedirs(branch_dir, exist_ok=True)
    success_count = 0
    for category, file_info in files_info.items():
        excel_filename = os.path.splitext(os.path.basename(file_info['csv_path']))[0] + '.xlsx'
        if _convert_single_to_excel(file_info, os.path.join(branch_dir, excel_filename), branch, category):
            success_count += 1
    return success_count


def get_timestamp() -> str:
    """Get current timestamp string for file naming."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def extract_base_name(filename: str, branch: str) -> str:
    """Extract base name from analytics filename without branch suffix."""
    base = os.path.splitext(filename)[0]
    return base.replace(f'_{branch}_analytics', '')


# =============================================================================
# DATAFRAME PROCESSING HELPERS
# =============================================================================

def _process_category_dataframe(dataframe: pd.DataFrame, category: str) -> pd.DataFrame:
    """Filter, sort and clean category DataFrame."""
    category_dataframe = dataframe[dataframe['product_type'] == category].copy()
    
    if len(category_dataframe) == 0:
        return None
    
    category_dataframe = category_dataframe.sort_values('product_name', ascending=True, key=lambda column: column.str.lower())
    return category_dataframe.drop('product_type', axis=1)


# =============================================================================
# CSV FILE I/O HELPERS
# =============================================================================

def _write_category_csv(category_dataframe: pd.DataFrame, file_path: str, has_date_header: bool, first_line: str) -> None:
    """Write category DataFrame to CSV file."""
    with open(file_path, 'w', encoding='utf-8-sig', newline='') as file_handle:
        if has_date_header:
            file_handle.write(first_line + '\n')
        category_dataframe.to_csv(file_handle, index=False, lineterminator='\n')


def _save_category_file(category_dataframe, branch_dir: str, base_name: str, branch: str, 
                        timestamp: str, category: str, has_date_header: bool, first_line: str) -> dict:
    """Save category DataFrame and return file info."""
    filename = f"{base_name}_{branch}_remaining_surplus_{timestamp}_{category}.csv"
    file_path = os.path.join(branch_dir, filename)
    _write_category_csv(category_dataframe, file_path, has_date_header, first_line)
    return {'csv_path': file_path, 'df': category_dataframe, 'has_date_header': has_date_header, 'first_line': first_line}


# =============================================================================
# EXCEL CONVERSION HELPERS
# =============================================================================

def _convert_single_to_excel(file_info: dict, excel_path: str, branch: str, category: str) -> bool:
    """Convert a single CSV file info to Excel."""
    try:
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            file_info['df'].to_excel(writer, index=False, sheet_name='Remaining Surplus')
        return True
    except Exception as error:
        logger.error("Error creating Excel file for %s/%s: %s", branch, category, error)
        return False
