"""Validation helpers for Step 11."""

import os
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_11.runner.constants import (
    TRANSFERS_DIR, 
    REMAINING_SURPLUS_DIR,
    OUTPUT_MERGED_CSV,
    OUTPUT_MERGED_EXCEL,
    OUTPUT_SEPARATE_CSV,
    OUTPUT_SEPARATE_EXCEL
)

logger = get_logger(__name__)


def validate_input_directories() -> bool:
    """Validate that required input directories exist."""
    if not os.path.exists(TRANSFERS_DIR):
        logger.error(
            f"Transfers directory not found: {TRANSFERS_DIR}\n"
            "Please run Step 7 (Generate Transfer Files) first"
        )
        return False
    if not os.path.exists(REMAINING_SURPLUS_DIR):
        logger.error(
            f"Remaining surplus directory not found: {REMAINING_SURPLUS_DIR}\n"
            "Please run Step 9 (Generate Remaining Surplus) first"
        )
        return False
    return True


def create_output_directories() -> None:
    """Create output directories if they don't exist."""
    for directory_path in [
        OUTPUT_MERGED_CSV, OUTPUT_MERGED_EXCEL, 
        OUTPUT_SEPARATE_CSV, OUTPUT_SEPARATE_EXCEL
    ]:
        os.makedirs(directory_path, exist_ok=True)
