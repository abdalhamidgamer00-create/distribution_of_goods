"""Step 8: Split transfer files by product type handler"""

import os
from src.shared.utils.file_handler import get_csv_files, get_latest_file
from src.services.transfers.splitters.file_splitter import split_all_transfer_files
from src.core.domain.classification.product_classifier import get_product_categories
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _find_transfer_files(transfers_base_dir: str) -> list:
    """Find all transfer CSV files that haven't been split yet."""
    categories = get_product_categories()
    transfer_files = []
    
    for root, dirs, files in os.walk(transfers_base_dir):
        for file in files:
            if not file.endswith('.csv'):
                continue
            
            is_split_file = any(file.endswith(f'_{cat}.csv') for cat in categories) or \
                           any(file == f'{cat}.csv' for cat in categories)
            if not is_split_file:
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
    except Exception:
        pass
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


def step_8_split_by_product_type(use_latest_file: bool = None) -> bool:
    """Step 8: Split transfer files by product type."""
    transfers_base_dir = os.path.join("data", "output", "transfers", "csv")
    
    if not os.path.exists(transfers_base_dir):
        logger.error("Transfers directory not found: %s", transfers_base_dir)
        logger.error("Please run step 6 (Generate Transfer Files) first to generate transfer files")
        return False
    
    transfer_files = _find_transfer_files(transfers_base_dir)
    
    if not transfer_files:
        logger.error("No transfer files found in %s", transfers_base_dir)
        logger.error("Please run step 6 (Generate Transfer Files) first to generate transfer files")
        return False
    
    try:
        has_date_header, first_line = _extract_date_header(transfer_files[0])
        
        logger.info("Splitting transfer files by product type...")
        logger.info("-" * 50)
        logger.info("Found %s transfer files to split", len(transfer_files))
        
        all_output_files = split_all_transfer_files(transfers_base_dir, has_date_header, first_line)
        
        if not all_output_files:
            logger.warning("No files were split")
            return False
        
        categories = get_product_categories()
        _log_split_summary(all_output_files, categories)
        logger.info("Split files saved to: %s", transfers_base_dir)
        
        logger.info("-" * 50)
        logger.info("Starting Excel conversion...")
        return _convert_to_excel(transfers_base_dir)
        
    except Exception as e:
        logger.exception("Error during file splitting: %s", e)
        return False



def _convert_to_excel(transfers_base_dir: str) -> bool:
    """Convert split transfer CSV files to Excel format"""
    from src.services.transfers.converters.excel_converter import convert_all_split_files_to_excel
    
    excel_output_dir = os.path.join("data", "output", "transfers", "excel")
    
    # Find all split CSV files
    split_files = []
    categories = get_product_categories()
    for root, dirs, files in os.walk(transfers_base_dir):
        for file in files:
            if file.endswith('.csv'):
                # Only process split category files (files ending with category name)
                is_split_file = any(file.endswith(f'_{cat}.csv') for cat in categories)
                if is_split_file:
                    split_files.append(os.path.join(root, file))
    
    if not split_files:
        logger.error("No split CSV files found in %s", transfers_base_dir)
        return False
    
    try:
        has_date_header = False
        first_line = ""
        
        try:
            sample_file = split_files[0]
            with open(sample_file, 'r', encoding='utf-8-sig') as f:
                first_line = f.readline().strip()
                from src.core.validation.data_validator import extract_dates_from_header
                start_date, end_date = extract_dates_from_header(first_line)
                if start_date and end_date:
                    has_date_header = True
        except Exception:
            pass
        
        logger.info("Converting split CSV files to Excel format...")
        logger.info("Found %s split CSV files to convert", len(split_files))
        
        excel_count = convert_all_split_files_to_excel(transfers_base_dir, excel_output_dir, has_date_header, first_line)
        
        if excel_count == 0:
            logger.warning("No Excel files were created")
            return False
        
        # Calculate statistics from created Excel files
        category_counts = {cat: 0 for cat in categories}
        
        # Count Excel files by category
        if os.path.exists(excel_output_dir):
            for root, dirs, files in os.walk(excel_output_dir):
                for file in files:
                    if file.endswith('.xlsx'):
                        for cat in categories:
                            if file.endswith(f'_{cat}.xlsx'):
                                category_counts[cat] = category_counts.get(cat, 0) + 1
                                break
        
        logger.info("Generated %s Excel files:", excel_count)
        for category in categories:
            count = category_counts[category]
            if count > 0:
                logger.info("  - %s: %s files", category, count)
        
        logger.info("Excel files saved to: %s", excel_output_dir)
        
        return True
        
    except Exception as e:
        logger.exception("Error during Excel conversion: %s", e)
        return False

