"""Step 3: Validate Data handler"""

import os
import pandas as pd
from src.shared.utils.file_handler import get_file_path, get_csv_files
from src.shared.utils.logging_utils import get_logger
from src.core.validation.data_validator import validate_csv_header, validate_csv_headers
from src.app.pipeline.utils.file_selector import select_csv_file

logger = get_logger(__name__)


def step_3_validate_data(use_latest_file: bool = None):
    """Step 3: Validate CSV data and date range"""
    # التحقق من الملف المُحوّل من Excel إلى CSV
    output_dir = os.path.join("data", "output", "converted", "csv")
    
    csv_files = get_csv_files(output_dir)
    
    if not csv_files:
        logger.error("No CSV files found in %s", output_dir)
        return False
    
    try:
        csv_file = select_csv_file(output_dir, csv_files, use_latest_file)
        csv_path = get_file_path(csv_file, output_dir)
        
        logger.info("Validating %s...", csv_file)
        logger.info("-" * 50)
        
        is_valid_date, start_date, end_date, date_message = validate_csv_header(csv_path)
        logger.info("[1] Date Range Validation: %s", date_message)
        if start_date and end_date:
            logger.info(
                "    Start: %s, End: %s",
                start_date.strftime('%d/%m/%Y %H:%M'),
                end_date.strftime('%d/%m/%Y %H:%M'),
            )
        logger.info(
            "    %s Date range is %s",
            "✓" if is_valid_date else "✗",
            ">= 3 months" if is_valid_date else "less than 3 months",
        )
        
        is_valid_headers, errors, headers_message = validate_csv_headers(csv_path)
        logger.info("[2] Column Headers Validation: %s", headers_message)
        if is_valid_headers:
            logger.info("    ✓ All column headers match expected order")
        else:
            logger.warning("    ✗ Column headers validation failed:")
            for error in errors:
                logger.warning("      - %s", error)
        
        overall_valid = is_valid_date and is_valid_headers
        logger.info("%s", "=" * 50)
        logger.info(
            "%s Overall validation: %s",
            "✓" if overall_valid else "✗",
            "SUCCESSFUL" if overall_valid else "FAILED",
        )
        logger.info("%s", "=" * 50)
        
        if overall_valid:
            logger.info("Removing first row (header with date range) from %s...", csv_file)
            try:
                df = pd.read_csv(csv_path, skiprows=1, encoding='utf-8-sig')
                df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                logger.info("✓ First row removed successfully")
            except Exception as e:
                logger.exception("✗ Error removing first row: %s", e)
                return False
        
        return overall_valid
        
    except ValueError:
        logger.error("Invalid input! Please enter a number.")
        return False
    except Exception as e:
        logger.exception("Error during validation: %s", e)
        return False

