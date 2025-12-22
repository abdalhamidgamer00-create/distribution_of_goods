"""Split transfer files by product type"""

import os
from datetime import datetime
import pandas as pd

from src.core.domain.classification.product_classifier import (
    classify_product_type,
    get_product_categories,
)
from src.shared.dataframes.validators import ensure_columns
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


# =============================================================================
# PUBLIC API
# =============================================================================

def split_transfer_file_by_type(transfer_file_path: str, output_dir: str,
                                has_date_header: bool = False, first_line: str = "") -> dict:
    """Split a transfer CSV file into multiple files by product type."""
    try:
        return _prepare_and_split(transfer_file_path, output_dir, has_date_header, first_line)
    except Exception as error:
        logger.exception("Error splitting file %s: %s", transfer_file_path, error)
        return {}


def split_all_transfer_files(transfers_base_dir: str, has_date_header: bool = False, first_line: str = "") -> dict:
    """Split all transfer files by product type."""
    all_output_files = {}
    categories = get_product_categories()
    
    for file_path in _find_unsplit_files(transfers_base_dir, categories):
        _process_transfer_file(file_path, transfers_base_dir, has_date_header, first_line, all_output_files)
    
    return all_output_files


# =============================================================================
# FILE NAME HELPERS
# =============================================================================

def _extract_target_branch(base_name: str) -> str:
    """Extract target branch name from file name."""
    if '_to_' in base_name:
        parts = base_name.split('_to_')
        if len(parts) > 1:
            return parts[-1]
    return None


def _get_folder_name(transfer_file_path: str, base_name: str) -> str:
    """Get folder name for output, adjusting for target branch."""
    base_folder_name = os.path.basename(os.path.dirname(transfer_file_path))
    target_branch = _extract_target_branch(base_name)
    
    if target_branch:
        return base_folder_name.replace('_to_other_branches', f'_to_{target_branch}')
    return base_folder_name


# =============================================================================
# FILE I/O HELPERS
# =============================================================================

def _write_csv_to_file(dataframe: pd.DataFrame, filepath: str, has_date_header: bool, first_line: str) -> None:
    """Write DataFrame to CSV with optional date header."""
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as file_handle:
        if has_date_header:
            file_handle.write(first_line + '\n')
        dataframe.to_csv(file_handle, index=False, lineterminator='\n')


def _save_category_file(category_dataframe: pd.DataFrame, file_folder: str, base_folder_name: str,
                        category: str, timestamp: str, has_date_header: bool, first_line: str) -> str:
    """Save a category DataFrame to CSV file."""
    category_dataframe = category_dataframe.drop('product_type', axis=1)
    category_dataframe = category_dataframe.sort_values('product_name', ascending=True, key=lambda column: column.str.lower())
    
    category_file = f"{base_folder_name}_{timestamp}_{category}.csv"
    category_path = os.path.join(file_folder, category_file)
    
    _write_csv_to_file(category_dataframe, category_path, has_date_header, first_line)
    return category_path


# =============================================================================
# DATAFRAME PREPARATION HELPERS
# =============================================================================

def _prepare_transfer_dataframe(transfer_file_path: str) -> pd.DataFrame:
    """Load and prepare transfer DataFrame with product types."""
    dataframe = pd.read_csv(transfer_file_path, encoding='utf-8-sig')
    ensure_columns(dataframe, ["code", "product_name", "quantity_to_transfer"], 
                  context=f"transfer file {transfer_file_path}")
    dataframe['product_type'] = dataframe['product_name'].apply(classify_product_type)
    return dataframe


# =============================================================================
# CATEGORY PROCESSING HELPERS
# =============================================================================

def _process_categories(dataframe: pd.DataFrame, file_folder: str, base_folder_name: str, 
                        timestamp: str, has_date_header: bool, first_line: str) -> dict:
    """Process each category and save to files."""
    output_files = {}
    for category in get_product_categories():
        category_dataframe = dataframe[dataframe['product_type'] == category].copy()
        if len(category_dataframe) > 0:
            output_files[category] = _save_category_file(
                category_dataframe, file_folder, base_folder_name, 
                category, timestamp, has_date_header, first_line
            )
    return output_files


def _prepare_and_split(transfer_file_path: str, output_dir: str, has_date_header: bool, first_line: str) -> dict:
    """Prepare transfer file and split by product type."""
    dataframe = _prepare_transfer_dataframe(transfer_file_path)
    base_name = os.path.splitext(os.path.basename(transfer_file_path))[0]
    base_folder_name = _get_folder_name(transfer_file_path, base_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_folder = os.path.join(output_dir, base_name)
    os.makedirs(file_folder, exist_ok=True)
    return _process_categories(dataframe, file_folder, base_folder_name, timestamp, has_date_header, first_line)


# =============================================================================
# BATCH PROCESSING HELPERS
# =============================================================================

def _is_already_split_file(filename: str, categories: list) -> bool:
    """Check if file is already a split category file."""
    return any(filename.endswith(f'_{category}.csv') for category in categories) or \
           any(filename == f'{category}.csv' for category in categories)


def _find_unsplit_files(transfers_base_dir: str, categories: list) -> list:
    """Find all unsplit transfer files."""
    unsplit = []
    for root, directories, files in os.walk(transfers_base_dir):
        for filename in files:
            if filename.endswith('.csv') and not _is_already_split_file(filename, categories):
                unsplit.append(os.path.join(root, filename))
    return unsplit


def _process_transfer_file(transfer_file_path: str, transfers_base_dir: str, has_date_header: bool, 
                            first_line: str, all_output_files: dict) -> None:
    """Process a single transfer file and add to results."""
    relative_path = os.path.relpath(transfer_file_path, transfers_base_dir)
    output_dir = os.path.dirname(os.path.join(transfers_base_dir, relative_path))
    split_files = split_transfer_file_by_type(transfer_file_path, output_dir, has_date_header, first_line)
    base_filename = os.path.splitext(os.path.basename(transfer_file_path))[0]
    for category, file_path in split_files.items():
        source_target = os.path.basename(os.path.dirname(transfer_file_path))
        all_output_files[(source_target, base_filename, category)] = file_path
