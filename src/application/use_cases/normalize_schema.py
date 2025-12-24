"""Use case for normalizing data schemas and renaming columns."""

import os
import re
from datetime import datetime
from src.shared.utils.logging_utils import get_logger
from src.shared.utils.file_handler import ensure_directory_exists
from src.services.conversion.converters.csv_column_renamer import (
    rename_csv_columns
)
from src.infrastructure.services.file_selector import FileSelectorService
from src.shared.config.paths import INPUT_CSV_DIR, RENAMED_CSV_DIR

logger = get_logger(__name__)


class NormalizeSchema:
    """Orchestrates conversion of inconsistent CSV headers to standard schema."""

    def __init__(self):
        self._input_directory = INPUT_CSV_DIR
        self._output_directory = RENAMED_CSV_DIR

    def execute(self, use_latest_file: bool = True, **kwargs) -> bool:
        """Selects a CSV file and normalizes its column headers."""
        ensure_directory_exists(self._output_directory)
        
        csv_name = FileSelectorService.select_csv_file(
            self._input_directory, use_latest=use_latest_file
        )
        if not csv_name:
            logger.error("No CSV file found for normalization.")
            return False

        input_path = os.path.join(self._input_directory, csv_name)
        output_path = self._get_target_path(csv_name)

        logger.info("Normalizing schema: %s -> %s", csv_name, output_path)
        return self._perform_normalization(input_path, output_path)

    def _get_target_path(self, original_filename: str) -> str:
        """Generates a clean, timestamped filename for normalized data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = os.path.splitext(original_filename)[0]
        # Remove any existing timestamps (8 digits _ 6 digits)
        clean_base = re.sub(r'_\d{8}_\d{6}', '', base)
        filename = f"{clean_base}_renamed_{timestamp}.csv"
        return os.path.join(self._output_directory, filename)

    def _perform_normalization(self, input_path: str, output_path: str) -> bool:
        """Calls the domain service to rename columns and log success."""
        try:
            rename_csv_columns(input_path, output_path)
            logger.info("✓ Data normalization completed successfully")
            return True
        except Exception as error:
            logger.exception(f"NormalizeSchema use case failed: {error}")
            return False
