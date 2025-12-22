"""Step 8: Split transfer files by product type handler"""

import os
from src.shared.utils.file_handler import get_csv_files, get_latest_file
from src.services.transfers.splitters.file_splitter import split_all_transfer_files
from src.core.domain.classification.product_classifier import get_product_categories
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _is_split_file(file: str, categories: list) -> bool:
    """Check if file is a split file."""
    return any(file.endswith(f'_{cat}.csv') for cat in categories) or any(file == f'{cat}.csv' for cat in categories)


def _find_transfer_files(transfers_base_dir: str) -> list:
    """Find all transfer CSV files that haven't been split yet."""
    categories = get_product_categories()
    transfer_files = []
    
    for root, dirs, files in os.walk(transfers_base_dir):
        for file in files:
            if file.endswith('.csv') and not _is_split_file(file, categories):
                transfer_files.append(os.path.join(root, file))
    
    return transfer_files


def _extract_date_header(sample_file: str) -> tuple:
    """Extract date header from sample file."""
    try:
        with open(sample_file, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline().strip()
        from src.core.validation.data_validator import extract_dates_from_header
        start_date, end_date = extract_dates_from_header(first_line)
        if start_date and end_date:
            return True, first_line
    except Exception: pass
    return False, ""


def _log_split_summary(all_output_files: dict, categories: list) -> None:
    """Log summary of split files."""
    category_counts = {cat: 0 for cat in categories}
    for (source_target, base_filename, category), file_path in all_output_files.items():
        category_counts[category] = category_counts.get(category, 0) + 1
    
    logger.info("Generated %s split files:", len(all_output_files))
    for category in categories:
        count = category_counts[category]
        if count > 0:
            logger.info("  - %s: %s files", category, count)


def _execute_split_and_log(transfer_files: list, transfers_base_dir: str, has_date_header: bool, first_line: str) -> bool:
    """Execute splitting and log results."""
    all_output_files = split_all_transfer_files(transfers_base_dir, has_date_header, first_line)
    if not all_output_files:
        logger.warning("No files were split")
        return False
    categories = get_product_categories()
    _log_split_summary(all_output_files, categories)
    logger.info("Split files saved to: %s", transfers_base_dir)
    return True


def _perform_split_and_convert(transfer_files: list, transfers_base_dir: str) -> bool:
    """Perform splitting and conversion to Excel."""
    has_date_header, first_line = _extract_date_header(transfer_files[0])
    logger.info("Splitting transfer files by product type...\n" + "-" * 50 + "\nFound %s transfer files to split", len(transfer_files))
    if not _execute_split_and_log(transfer_files, transfers_base_dir, has_date_header, first_line):
        return False
    logger.info("-" * 50 + "\nStarting Excel conversion...")
    return _convert_to_excel(transfers_base_dir)


def _validate_transfers_dir(transfers_base_dir: str) -> list:
    """Validate transfers directory and return transfer files."""
    if not os.path.exists(transfers_base_dir):
        logger.error("Transfers directory not found: %s", transfers_base_dir)
        logger.error("Please run step 6 (Generate Transfer Files) first to generate transfer files")
        return []
    
    transfer_files = _find_transfer_files(transfers_base_dir)
    if not transfer_files:
        logger.error("No transfer files found in %s", transfers_base_dir)
        logger.error("Please run step 6 (Generate Transfer Files) first to generate transfer files")
    return transfer_files


def step_8_split_by_product_type(use_latest_file: bool = None) -> bool:
    """Step 8: Split transfer files by product type."""
    transfers_base_dir = os.path.join("data", "output", "transfers", "csv")
    transfer_files = _validate_transfers_dir(transfers_base_dir)
    if not transfer_files:
        return False
    try:
        return _perform_split_and_convert(transfer_files, transfers_base_dir)
    except Exception as e:
        logger.exception("Error during file splitting: %s", e)
        return False



def _find_split_csv_files(transfers_base_dir: str) -> list:
    """Find all split CSV files (files ending with category name)."""
    categories = get_product_categories()
    split_files = []
    for root, dirs, files in os.walk(transfers_base_dir):
        for file in files:
            if file.endswith('.csv') and any(file.endswith(f'_{cat}.csv') for cat in categories):
                split_files.append(os.path.join(root, file))
    return split_files


def _count_single_excel(file: str, categories: list, category_counts: dict) -> None:
    """Count a single Excel file's category."""
    if file.endswith('.xlsx'):
        for cat in categories:
            if file.endswith(f'_{cat}.xlsx'):
                category_counts[cat] += 1
                break


def _count_excel_by_category(excel_output_dir: str) -> dict:
    """Count Excel files by category."""
    categories = get_product_categories()
    category_counts = {cat: 0 for cat in categories}
    if not os.path.exists(excel_output_dir):
        return category_counts
    for root, dirs, files in os.walk(excel_output_dir):
        for file in files:
            _count_single_excel(file, categories, category_counts)
    return category_counts


def _log_excel_summary(excel_count: int, excel_output_dir: str) -> None:
    """Log summary of generated Excel files."""
    categories = get_product_categories()
    category_counts = _count_excel_by_category(excel_output_dir)
    
    logger.info("Generated %s Excel files:", excel_count)
    for category in categories:
        count = category_counts[category]
        if count > 0:
            logger.info("  - %s: %s files", category, count)
    logger.info("Excel files saved to: %s", excel_output_dir)


def _log_and_convert(transfers_base_dir: str, excel_output_dir: str, split_files: list, 
                      has_date_header: bool, first_line: str) -> int:
    """Log info and perform conversion."""
    from src.services.transfers.converters.excel_converter import convert_all_split_files_to_excel
    logger.info("Converting split CSV files to Excel format...")
    logger.info("Found %s split CSV files to convert", len(split_files))
    return convert_all_split_files_to_excel(transfers_base_dir, excel_output_dir, has_date_header, first_line)


def _execute_excel_conversion(transfers_base_dir: str, excel_output_dir: str, 
                               split_files: list, has_date_header: bool, first_line: str) -> bool:
    """Execute the Excel conversion process."""
    excel_count = _log_and_convert(transfers_base_dir, excel_output_dir, split_files, has_date_header, first_line)
    
    if excel_count == 0:
        logger.warning("No Excel files were created")
        return False
    
    _log_excel_summary(excel_count, excel_output_dir)
    return True


def _try_convert_excel(split_files: list, transfers_base_dir: str, excel_output_dir: str) -> bool:
    """Try to convert files to Excel with error handling."""
    try:
        has_date_header, first_line = _extract_date_header(split_files[0])
        return _execute_excel_conversion(transfers_base_dir, excel_output_dir, split_files, has_date_header, first_line)
    except Exception as e:
        logger.exception("Error during Excel conversion: %s", e)
        return False


def _convert_to_excel(transfers_base_dir: str) -> bool:
    """Convert split transfer CSV files to Excel format."""
    from src.services.transfers.converters.excel_converter import convert_all_split_files_to_excel
    
    excel_output_dir = os.path.join("data", "output", "transfers", "excel")
    split_files = _find_split_csv_files(transfers_base_dir)
    
    if not split_files:
        logger.error("No split CSV files found in %s", transfers_base_dir)
        return False
    
    return _try_convert_excel(split_files, transfers_base_dir, excel_output_dir)


