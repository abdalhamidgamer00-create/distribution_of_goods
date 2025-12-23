"""Service for validating ingested stock data."""

import os
from src.shared.utils.file_handler import get_csv_files
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_3.validator import selection
from src.application.interfaces.repository import DataRepository

logger = get_logger(__name__)

class ValidationService:
    """Manages validation of CSV data, including headers and date ranges."""

    def __init__(self, repository: DataRepository):
        self._repository = repository
        self._converted_dir = os.path.join("data", "output", "converted", "csv")

    def execute(self, use_latest_file: bool = None) -> bool:
        """Validates CSV files in the converted directory."""
        csv_files = get_csv_files(self._converted_dir)
        
        if not csv_files:
            logger.error(f"No CSV files found in {self._converted_dir}")
            return False
        
        try:
            success = selection.try_validate(
                self._converted_dir, 
                csv_files, 
                use_latest_file
            )
            if success:
                logger.info("✓ Data validation completed successfully")
            else:
                logger.error("Data validation failed")
            return success
        except Exception as e:
            logger.exception(f"ValidationService failed: {e}")
            return False
