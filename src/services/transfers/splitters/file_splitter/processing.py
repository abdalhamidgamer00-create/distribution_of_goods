"""Processing and splitting logic."""

import os
from datetime import datetime
from src.core.domain.classification.product_classifier import (
    get_product_categories,
)
from src.shared.utils.logging_utils import get_logger
from src.services.transfers.splitters.file_splitter import paths, io

logger = get_logger(__name__)


def process_categories(
    dataframe, file_folder: str, base_folder_name: str, 
    timestamp: str, has_date_header: bool, first_line: str
) -> dict:
    """Process each category and save to files."""
    output_files = {}
    for category in get_product_categories():
        mask = dataframe['product_type'] == category
        category_dataframe = dataframe[mask].copy()
        
        if len(category_dataframe) > 0:
            output_files[category] = io.save_category_file(
                category_dataframe, file_folder, base_folder_name, 
                category, timestamp, has_date_header, first_line
            )
    return output_files


def prepare_and_split(
    transfer_file_path: str, output_dir: str, has_date_header: bool, 
    first_line: str
) -> dict:
    """Prepare transfer file and split by product type."""
    dataframe = io.prepare_transfer_dataframe(transfer_file_path)
    base_name = os.path.splitext(os.path.basename(transfer_file_path))[0]
    base_folder_name = paths.get_folder_name(transfer_file_path, base_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_folder = os.path.join(output_dir, base_name)
    os.makedirs(file_folder, exist_ok=True)
    
    return process_categories(
        dataframe, 
        file_folder, 
        base_folder_name, 
        timestamp, 
        has_date_header, 
        first_line
    )


def split_transfer_file_by_type(
    transfer_file_path: str, output_dir: str,
    has_date_header: bool = False, first_line: str = ""
) -> dict:
    """Split a transfer CSV file into multiple files by product type."""
    try:
        return prepare_and_split(
            transfer_file_path, output_dir, has_date_header, first_line
        )
    except Exception as error:
        logger.exception(
            "Error splitting file %s: %s", transfer_file_path, error
        )
        return {}
