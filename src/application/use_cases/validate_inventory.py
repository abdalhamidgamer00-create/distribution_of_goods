"""Use case for validating inventory data integrity and schema."""

import os
from src.shared.utils.logging_utils import get_logger
from src.domain.services.validation import (
    validate_csv_header, validate_csv_headers
)
from src.infrastructure.services.file_selector import FileSelectorService
from src.shared.config.paths import INPUT_CSV_DIR

logger = get_logger(__name__)


class ValidateInventory:
    """Orchestrates the validation of ingested CSV inventory data."""

    def __init__(self):
        self._input_directory = INPUT_CSV_DIR

    def execute(self, use_latest_file: bool = True, **kwargs) -> bool:
        """Selects a CSV file and validates its headers and date range."""
        csv_name = FileSelectorService.select_csv_file(
            self._input_directory, use_latest=use_latest_file
        )
        
        if not csv_name:
            logger.error("No CSV file found for validation.")
            return False

        path = os.path.join(self._input_directory, csv_name)
        logger.info("Validating inventory data: %s", csv_name)

        self._run_date_validation(path)
        is_valid_schema = self._run_schema_validation(path)
        
        self._log_result(is_valid_schema, csv_name)
        return is_valid_schema

    def _run_date_validation(self, csv_path: str) -> None:
        """Validates the date range reported in the CSV header."""
        is_valid, start, end, message = validate_csv_header(csv_path)
        if is_valid:
            logger.info("✓ Date range validated: %s to %s", start, end)
        else:
            logger.warning("! Date validation issue: %s", message)

    def _run_schema_validation(self, csv_path: str) -> bool:
        """Validates that the CSV contains all required headers."""
        is_valid, missing, message = validate_csv_headers(csv_path)
        if is_valid:
            logger.info("✓ Schema headers validated")
        else:
            logger.error("✗ Schema validation failed: %s", message)
            if missing:
                logger.error("  Missing headers: %s", ", ".join(missing))
        return is_valid

    def _log_result(self, success: bool, filename: str) -> None:
        """Logs the final outcome of the validation process."""
        if success:
            logger.info("✓ Data validation completed successfully")
        else:
            logger.error("Data validation failed for: %s", filename)
