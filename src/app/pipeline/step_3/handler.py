"""Step 3: Validate Data handler"""

import os
import pandas as pd
from src.shared.utils.file_handler import get_file_path, get_csv_files
from src.shared.utils.logging_utils import get_logger
from src.core.validation import validate_csv_header, validate_csv_headers
from src.app.pipeline.utils.file_selector import select_csv_file

logger = get_logger(__name__)


# =============================================================================
# PUBLIC API
# =============================================================================

def step_3_validate_data(use_latest_file: bool = None):
    """Step 3: Validate CSV data and date range."""
    output_dir = os.path.join("data", "output", "converted", "csv")
    csv_files = get_csv_files(output_dir)
    
    if not csv_files:
        logger.error("No CSV files found in %s", output_dir)
        return False
    
    return _try_validate(output_dir, csv_files, use_latest_file)


# =============================================================================
# DATE LOGGING HELPERS
# =============================================================================

def _log_date_validation(is_valid: bool, start_date, end_date, message: str) -> None:
    """Log date range validation results."""
    logger.info("[1] Date Range Validation: %s", message)
    if start_date and end_date:
        logger.info("    Start: %s, End: %s", 
                   start_date.strftime('%d/%m/%Y %H:%M'),
                   end_date.strftime('%d/%m/%Y %H:%M'))
    status = ">= 3 months" if is_valid else "less than 3 months"
    logger.info("    %s Date range is %s", "✓" if is_valid else "✗", status)


# =============================================================================
# HEADERS LOGGING HELPERS
# =============================================================================

def _log_headers_validation(is_valid: bool, errors: list, message: str) -> None:
    """Log column headers validation results."""
    logger.info("[2] Column Headers Validation: %s", message)
    if is_valid:
        logger.info("    ✓ All column headers match expected order")
    else:
        logger.warning("    ✗ Column headers validation failed:")
        for error in errors:
            logger.warning("      - %s", error)


def _log_overall_result(is_valid: bool) -> None:
    """Log overall validation result."""
    logger.info("=" * 50)
    result = "SUCCESSFUL" if is_valid else "FAILED"
    logger.info("%s Overall validation: %s", "✓" if is_valid else "✗", result)
    logger.info("=" * 50)


# =============================================================================
# FILE MODIFICATION HELPERS
# =============================================================================

def _remove_first_row(csv_path: str, csv_file: str) -> bool:
    """Remove first row (header with date range) from CSV file."""
    logger.info("Removing first row (header with date range) from %s...", csv_file)
    try:
        dataframe = pd.read_csv(csv_path, skiprows=1, encoding='utf-8-sig')
        dataframe.to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info("✓ First row removed successfully")
        return True
    except Exception as error:
        logger.exception("✗ Error removing first row: %s", error)
        return False


# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def _perform_validation(csv_path: str) -> tuple:
    """Perform date and headers validation."""
    is_valid_date, start_date, end_date, date_message = validate_csv_header(csv_path)
    _log_date_validation(is_valid_date, start_date, end_date, date_message)
    
    is_valid_headers, errors, headers_message = validate_csv_headers(csv_path)
    _log_headers_validation(is_valid_headers, errors, headers_message)
    
    return is_valid_date and is_valid_headers


def _handle_post_validation(overall_valid: bool, csv_path: str, csv_file: str) -> bool:
    """Handle post-validation actions."""
    _log_overall_result(overall_valid)
    
    if overall_valid and not _remove_first_row(csv_path, csv_file):
        return False
    return overall_valid


def _validate_csv_file(output_dir: str, csv_files: list, use_latest_file: bool) -> bool:
    """Validate a selected CSV file."""
    csv_file = select_csv_file(output_dir, csv_files, use_latest_file)
    csv_path = get_file_path(csv_file, output_dir)
    
    logger.info("Validating %s...", csv_file)
    logger.info("-" * 50)
    
    overall_valid = _perform_validation(csv_path)
    return _handle_post_validation(overall_valid, csv_path, csv_file)


def _try_validate(output_dir: str, csv_files: list, use_latest_file: bool) -> bool:
    """Try to validate files with error handling."""
    try:
        return _validate_csv_file(output_dir, csv_files, use_latest_file)
    except ValueError:
        logger.error("Invalid input! Please enter a number.")
        return False
    except Exception as error:
        logger.exception("Error during validation: %s", error)
        return False
