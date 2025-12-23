"""Main orchestrator for Step 11."""

from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_11.combiner import get_timestamp
from src.app.pipeline.step_11.runner import validation, processing
from src.app.pipeline.step_11.runner.constants import (
    OUTPUT_MERGED_EXCEL,
    OUTPUT_SEPARATE_EXCEL,
)

logger = get_logger(__name__)


def log_summary(total_merged: int, total_separate: int) -> None:
    """Log summary of generated files."""
    logger.info(
        "=" * 50 + 
        f"\nGenerated {total_merged} merged files (CSV + Excel)\n"
        f"Generated {total_separate} separate files (CSV + Excel)\n"
        f"Merged output: {OUTPUT_MERGED_EXCEL}\n"
        f"Separate output: {OUTPUT_SEPARATE_EXCEL}"
    )


def step_11_generate_combined_transfers(use_latest_file: bool = None) -> bool:
    """Step 11: Generate combined transfer files with remaining surplus."""
    if not validation.validate_input_directories():
        return False
    validation.create_output_directories()
    try:
        total_merged, total_separate = processing.process_all_branches(
            get_timestamp()
        )
        log_summary(total_merged, total_separate)
        return total_merged > 0 or total_separate > 0
    except Exception as error:
        logger.exception(f"Error generating combined transfer files: {error}")
        return False
