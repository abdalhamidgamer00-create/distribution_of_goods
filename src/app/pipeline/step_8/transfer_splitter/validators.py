"""Validation and file finding utilities for Step 8."""

import os
from src.shared.utils.logging_utils import get_logger
from src.core.domain.classification.product_classifier import (
    get_product_categories,
)
from src.core.validation import extract_dates_from_header

logger = get_logger(__name__)


def validate_transfers_directory(transfers_base_dir: str) -> list:
    """Validate transfers directory and return transfer files."""
    if not os.path.exists(transfers_base_dir):
        logger.error("Transfers directory not found: %s", transfers_base_dir)
        logger.error(
            "Please run step 6 (Generate Transfer Files) first to generate "
            "transfer files"
        )
        return []
    
    transfer_files = find_transfer_files(transfers_base_dir)
    if not transfer_files:
        logger.error("No transfer files found in %s", transfers_base_dir)
        logger.error(
            "Please run step 6 (Generate Transfer Files) first to generate "
            "transfer files"
        )
    return transfer_files


def is_split_file(file: str, categories: list) -> bool:
    """Check if file is a split file."""
    return any(
        file.endswith(f'_{category}.csv') for category in categories
    ) or any(file == f'{category}.csv' for category in categories)


def find_transfer_files(transfers_base_dir: str) -> list:
    """Find all transfer CSV files that haven't been split yet."""
    categories = get_product_categories()
    transfer_files = []
    
    for root, _, files in os.walk(transfers_base_dir):
        for file in files:
            if file.endswith('.csv') and not is_split_file(file, categories):
                transfer_files.append(os.path.join(root, file))
    
    return transfer_files


def find_split_csv_files(transfers_base_dir: str) -> list:
    """Find all split CSV files (files ending with category name)."""
    categories = get_product_categories()
    split_files = []
    for root, _, files in os.walk(transfers_base_dir):
        for file in files:
            if file.endswith('.csv') and any(
                file.endswith(f'_{category}.csv') for category in categories
            ):
                split_files.append(os.path.join(root, file))
    return split_files


def extract_date_header(sample_file: str) -> tuple:
    """Extract date header from sample file."""
    try:
        with open(sample_file, 'r', encoding='utf-8-sig') as file_handle:
            first_line = file_handle.readline().strip()
        
        start_date, end_date = extract_dates_from_header(first_line)
        if start_date and end_date:
            return True, first_line
    except Exception:
        pass
    return False, ""
