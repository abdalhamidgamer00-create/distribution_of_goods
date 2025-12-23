"""Use case for normalizing data schemas and renaming columns."""

import os
import re
from datetime import datetime
from src.shared.utils.logging_utils import get_logger
from src.shared.utils.file_handler import ensure_directory_exists
from src.services.conversion.converters.csv_column_renamer import rename_csv_columns
from src.infrastructure.services.file_selector import FileSelectorService

logger = get_logger(__name__)

class NormalizeSchema:
    """Orchestrates the conversion of inconsistent CSV headers to a standard schema."""

    def __init__(self):
        self._input_directory = os.path.join("data", "output", "converted", "csv")
        self._output_directory = os.path.join("data", "output", "converted", "renamed")

    def execute(self, use_latest_file: bool = True, **kwargs) -> bool:
        """
        Selects a CSV file and normalizes its column headers.
        
        Args:
            use_latest_file: If True, automatically selects the newest file.
            **kwargs: Additional arguments.
        """
        ensure_directory_exists(self._output_directory)
        
        csv_filename = FileSelectorService.select_csv_file(self._input_directory, use_latest=use_latest_file)
        
        if not csv_filename:
            logger.error("No CSV file found for normalization in %s", self._input_directory)
            return False

        input_path = os.path.join(self._input_directory, csv_filename)
        output_filename = self._generate_output_filename(csv_filename)
        output_path = os.path.join(self._output_directory, output_filename)

        logger.info("Normalizing schema: %s -> %s", csv_filename, output_filename)

        try:
            rename_csv_columns(input_path, output_path)
            logger.info("✓ Data normalization completed successfully")
            return True
        except Exception as e:
            logger.exception(f"NormalizeSchema use case failed: {e}")
            return False

    def _generate_output_filename(self, original_filename: str) -> str:
        """Generates a clean, timestamped filename for normalized data."""
        timestamp_string = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(original_filename)[0]
        # Remove any existing timestamps
        base_name_clean = re.sub(r'_\d{8}_\d{6}', '', base_name)
        return f"{base_name_clean}_renamed_{timestamp_string}.csv"
