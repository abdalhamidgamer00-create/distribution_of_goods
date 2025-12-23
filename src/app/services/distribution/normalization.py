"""Service for normalizing data schemas and renaming columns."""

import os
import re
from datetime import datetime
from src.shared.utils.file_handler import (
    get_file_path, get_csv_files, ensure_directory_exists
)
from src.services.conversion.converters.csv_column_renamer import (
    rename_csv_columns
)
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.utils.file_selector import select_csv_file
from src.application.interfaces.repository import DataRepository

logger = get_logger(__name__)

class NormalizationService:
    """Manages the translation of raw CSV headers into a standardized schema."""

    def __init__(self, repository: DataRepository):
        self._repository = repository
        self._input_dir = os.path.join("data", "output", "converted", "csv")
        self._output_dir = os.path.join("data", "output", "converted", "renamed")

    def execute(self, use_latest_file: bool = None) -> bool:
        """Standardizes CSV columns and saves the result to the renamed directory."""
        ensure_directory_exists(self._output_dir)
        
        csv_files = get_csv_files(self._input_dir)
        if not csv_files:
            logger.error(f"No CSV files found in {self._input_dir}")
            return False
        
        try:
            csv_file = select_csv_file(self._input_dir, csv_files, use_latest_file)
            input_path = get_file_path(csv_file, self._input_dir)
            
            output_file = self._generate_filename(csv_file)
            output_path = get_file_path(output_file, self._output_dir)
            
            logger.info(f"Normalizing schema in {csv_file}...")
            rename_csv_columns(input_path, output_path)
            
            logger.info(f"✓ Data normalization completed: {output_file}")
            return True
        except Exception as e:
            logger.exception(f"NormalizationService failed: {e}")
            return False

    def _generate_filename(self, csv_file: str) -> str:
        """Generates a timestamped filename for normalized data."""
        date_string = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.splitext(csv_file)[0]
        base_name_only = os.path.basename(base_name)
        base_name_clean = re.sub(r'_\d{8}_\d{6}', '', base_name_only)
        return f"{base_name_clean}_renamed_{date_string}.csv"
