"""Main orchestrator for step 3."""

import os
from src.shared.utils.file_handler import get_csv_files
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_3.validator import selection

logger = get_logger(__name__)


def step_3_validate_data(use_latest_file: bool = None):
    """Step 3: Validate CSV data and date range."""
    output_dir = os.path.join("data", "output", "converted", "csv")
    csv_files = get_csv_files(output_dir)
    
    if not csv_files:
        logger.error("No CSV files found in %s", output_dir)
        return False
    
    return selection.try_validate(output_dir, csv_files, use_latest_file)
