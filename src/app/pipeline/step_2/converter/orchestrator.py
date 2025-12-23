"""Orchestration logic."""

import os
from src.shared.utils.file_handler import ensure_directory_exists
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_2.converter.core import try_convert_excel

logger = get_logger(__name__)

def step_2_convert_excel_to_csv(use_latest_file: bool = None):
    """Step 2: Convert Excel to CSV."""
    input_dir = os.path.join("data", "input")
    converted_dir = os.path.join("data", "output", "converted", "csv")
    ensure_directory_exists(converted_dir)
    
    try:
        return try_convert_excel(input_dir, converted_dir, use_latest_file)
    except (ValueError, Exception) as error:
        logger.exception("Error during conversion: %s", error)
        return False
