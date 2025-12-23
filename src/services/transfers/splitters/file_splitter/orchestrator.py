"""High-level orchestrator for file splitting."""

import os
from src.core.domain.classification.product_classifier import (
    get_product_categories,
)
from src.services.transfers.splitters.file_splitter import paths, processing


def process_transfer_file(
    transfer_file_path: str, 
    transfers_base_dir: str, 
    has_date_header: bool, 
    first_line: str, 
    all_output_files: dict
) -> None:
    """Process a single transfer file and add to results."""
    relative_path = os.path.relpath(transfer_file_path, transfers_base_dir)
    joined_path = os.path.join(transfers_base_dir, relative_path)
    output_dir = os.path.dirname(joined_path)
    
    split_files = processing.split_transfer_file_by_type(
        transfer_file_path, output_dir, has_date_header, first_line
    )
    base_name = os.path.splitext(os.path.basename(transfer_file_path))[0]
    
    for category, file_path in split_files.items():
        source_target = os.path.basename(os.path.dirname(transfer_file_path))
        all_output_files[(source_target, base_name, category)] = file_path


def split_all_transfer_files(
    transfers_base_dir: str, 
    has_date_header: bool = False, 
    first_line: str = ""
) -> dict:
    """Split all transfer files by product type."""
    all_output_files = {}
    categories = get_product_categories()
    
    for file_path in paths.find_unsplit_files(transfers_base_dir, categories):
        process_transfer_file(
            file_path, 
            transfers_base_dir, 
            has_date_header, 
            first_line, 
            all_output_files
        )
    
    return all_output_files
