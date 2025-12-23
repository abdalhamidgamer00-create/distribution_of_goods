"""Refactored Handler for Step 11: Generate Combined Transfer Files."""

import os
from datetime import datetime
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_11.runner import processing, validation

logger = get_logger(__name__)

def step_11_generate_combined_transfers(use_latest_file: bool = None, **kwargs) -> bool:
    """
    Step 11: Generate combined transfer files with remaining surplus.
    Utilizes Clean Architecture components and enhanced repository support.
    """
    if not validation.validate_input_directories():
        return False
        
    validation.create_output_directories()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        total_merged, total_separate = processing.process_all_branches(timestamp)
        log_summary(total_merged, total_separate)
        return (total_merged + total_separate) > 0
    except Exception as e:
        logger.exception(f"Error in Step 11: {e}")
        return False

def log_summary(merged_count: int, separate_count: int) -> None:
    """Logs a summary of generated files."""
    logger.info("=" * 50)
    logger.info(f"Generated {merged_count} merged files (CSV + Excel)")
    logger.info(f"Generated {separate_count} separate files (CSV + Excel)")
    logger.info("Merged output: data/output/combined_transfers/merged/excel")
    logger.info("Separate output: data/output/combined_transfers/separate/excel")
