"""Orchestrator for Step 8 transfer file splitting and conversion."""

import os
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_8.transfer_splitter import (
    validators,
    processors,
    converters,
)

logger = get_logger(__name__)


def perform_split_and_convert(
    transfer_files: list, 
    transfers_base_dir: str
) -> bool:
    """Perform splitting and conversion to Excel."""
    has_date_header, first_line = validators.extract_date_header(
        transfer_files[0]
    )
    
    logger.info(
        "Splitting transfer files by product type...\n" + 
        "-" * 50 + 
        "\nFound %s transfer files to split", 
        len(transfer_files)
    )
    
    if not processors.execute_split_and_log(
        transfers_base_dir, has_date_header, first_line
    ):
        return False
        
    logger.info("-" * 50 + "\nStarting Excel conversion...")
    return converters.convert_to_excel(transfers_base_dir)


def run_split_by_product_type() -> bool:
    """Run Step 8: Split transfer files by product type."""
    transfers_base_dir = os.path.join("data", "output", "transfers", "csv")
    transfer_files = validators.validate_transfers_directory(transfers_base_dir)
    
    if not transfer_files:
        return False
        
    try:
        return perform_split_and_convert(transfer_files, transfers_base_dir)
    except Exception as error:
        logger.exception("Error during file splitting: %s", error)
        return False
