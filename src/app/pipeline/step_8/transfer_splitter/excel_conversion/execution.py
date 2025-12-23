"""Excel conversion execution logic."""

import os
from src.shared.utils.logging_utils import get_logger
from src.services.transfers.converters.excel_converter import (
    convert_all_split_files_to_excel
)
from src.app.pipeline.step_8.transfer_splitter.validators import (
    find_split_csv_files, 
    extract_date_header
)
from .counting import (
    log_excel_summary
)

logger = get_logger(__name__)


def log_and_convert(
    transfers_base_dir: str, 
    excel_output_dir: str, 
    split_files: list, 
    has_date_header: bool, 
    first_line: str
) -> int:
    """Log info and perform conversion."""
    logger.info("Converting split CSV files to Excel format...")
    logger.info("Found %s split CSV files to convert", len(split_files))
    return convert_all_split_files_to_excel(
        transfers_base_dir, excel_output_dir, has_date_header, first_line
    )


def execute_excel_conversion(
    transfers_base_dir: str, 
    excel_output_dir: str, 
    split_files: list, 
    has_date_header: bool, 
    first_line: str
) -> bool:
    """Execute the Excel conversion process."""
    excel_count = log_and_convert(
        transfers_base_dir, 
        excel_output_dir, 
        split_files, 
        has_date_header, 
        first_line
    )
    
    if excel_count == 0:
        logger.warning("No Excel files were created")
        return False
    
    log_excel_summary(excel_count, excel_output_dir)
    return True


def try_convert_to_excel(
    split_files: list, 
    transfers_base_dir: str, 
    excel_output_dir: str
) -> bool:
    """Try to convert files to Excel with error handling."""
    try:
        has_date_header, first_line = extract_date_header(split_files[0])
        return execute_excel_conversion(
            transfers_base_dir, 
            excel_output_dir, 
            split_files, 
            has_date_header, 
            first_line
        )
    except Exception as error:
        logger.exception("Error during Excel conversion: %s", error)
        return False


def convert_to_excel(transfers_base_dir: str) -> bool:
    """Convert split transfer CSV files to Excel format."""
    excel_output_dir = os.path.join("data", "output", "transfers", "excel")
    split_files = find_split_csv_files(transfers_base_dir)
    if not split_files:
        logger.error("No split CSV files found in %s", transfers_base_dir)
        return False
    return try_convert_to_excel(
        split_files, transfers_base_dir, excel_output_dir
    )
