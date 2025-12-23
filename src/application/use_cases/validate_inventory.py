"""Use case for validating inventory data integrity and schema."""

import os
from src.shared.utils.logging_utils import get_logger
from src.core.validation import validate_csv_header, validate_csv_headers
from src.infrastructure.services.file_selector import FileSelectorService

logger = get_logger(__name__)

class ValidateInventory:
    """Orchestrates the validation of ingested CSV inventory data."""

    def __init__(self):
        self._input_directory = os.path.join("data", "output", "converted", "csv")

    def execute(self, use_latest_file: bool = True, **kwargs) -> bool:
        """
        Selects a CSV file and validates its headers and date range.
        
        Args:
            use_latest_file: If True, automatically selects the newest file.
            **kwargs: Additional arguments.
        """
        csv_filename = FileSelectorService.select_csv_file(self._input_directory, use_latest=use_latest_file)
        
        if not csv_filename:
            logger.error("No CSV file found for validation in %s", self._input_directory)
            return False

        csv_path = os.path.join(self._input_directory, csv_filename)
        logger.info("Validating inventory data: %s", csv_filename)

        # 1. Validate Date Range
        is_valid_date, start_date, end_date, date_message = validate_csv_header(csv_path)
        if is_valid_date:
            logger.info("✓ Date range validated: %s to %s", start_date, end_date)
        else:
            logger.warning("! Date validation issue: %s", date_message)

        # 2. Validate Headers
        is_valid_headers, missing_headers, headers_message = validate_csv_headers(csv_path)
        if is_valid_headers:
            logger.info("✓ Schema headers validated")
        else:
            logger.error("✗ Schema validation failed: %s", headers_message)
            if missing_headers:
                logger.error("  Missing headers: %s", ", ".join(missing_headers))

        success = is_valid_headers  # Only headers are critical for following steps
        
        if success:
            logger.info("✓ Data validation completed successfully")
        else:
            logger.error("Data validation failed for: %s", csv_filename)
            
        return success
