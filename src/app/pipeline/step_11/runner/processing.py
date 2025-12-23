"""Branch processing helpers for Step 11."""

from src.core.domain.branches.config import get_branches
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_11.combiner import combine_transfers_and_surplus
from src.app.pipeline.step_11.runner.constants import (
    TRANSFERS_DIR,
    REMAINING_SURPLUS_DIR,
    ANALYTICS_DIR,
)
from src.app.pipeline.step_11.runner import generators

logger = get_logger(__name__)


def get_combined_data(branch: str):
    """Get combined data for a branch."""
    return combine_transfers_and_surplus(
        branch=branch, transfers_dir=TRANSFERS_DIR,
        surplus_dir=REMAINING_SURPLUS_DIR, analytics_dir=ANALYTICS_DIR,
    )


def process_single_branch(branch: str, timestamp: str) -> tuple:
    """Process a single branch and return (merged_count, separate_count)."""
    logger.info(f"Processing branch: {branch}")
    combined_data = get_combined_data(branch)
    
    if combined_data is None or combined_data.empty:
        logger.warning(f"No data to combine for branch: {branch}")
        return 0, 0
    
    return (
        generators.generate_merged_output(combined_data, branch, timestamp),
        generators.generate_separate_output(combined_data, branch, timestamp)
    )


def process_all_branches(timestamp: str) -> tuple:
    """Process all branches and return total counts."""
    total_merged = 0
    total_separate = 0
    for branch in get_branches():
        merged, separate = process_single_branch(branch, timestamp)
        total_merged += merged
        total_separate += separate
    return total_merged, total_separate
