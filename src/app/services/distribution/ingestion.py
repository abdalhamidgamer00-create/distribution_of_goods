"""Service for ingesting and converting raw source data."""

import os
from src.shared.utils.file_handler import ensure_directory_exists
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_2.converter.core import try_convert_excel
from src.application.interfaces.repository import DataRepository

logger = get_logger(__name__)

class IngestionService:
    """Manages conversion of raw Excel input into internal CSV format."""

    def __init__(self, repository: DataRepository):
        self._repository = repository
        self._input_dir = os.path.join("data", "input")
        self._converted_dir = os.path.join("data", "output", "converted", "csv")

    def execute(self, use_latest_file: bool = None) -> bool:
        """Converts Excel files from input directory to CSV."""
        ensure_directory_exists(self._converted_dir)
        
        try:
            success = try_convert_excel(
                self._input_dir, 
                self._converted_dir, 
                use_latest_file
            )
            if success:
                logger.info("✓ Data ingestion completed successfully")
            else:
                logger.error("Data ingestion failed")
            return success
        except Exception as e:
            logger.exception(f"IngestionService failed: {e}")
            return False
