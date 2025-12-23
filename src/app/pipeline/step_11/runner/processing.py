"""Branch processing helpers for Step 11."""

from src.core.domain.branches.config import get_branches
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_11.runner.constants import (
    TRANSFERS_DIR,
    REMAINING_SURPLUS_DIR,
    ANALYTICS_DIR,
)

logger = get_logger(__name__)


def get_combined_data(branch: str):
    """Legacy helper for tests."""
    from src.app.pipeline.step_11.combiner import combine_transfers_and_surplus
    return combine_transfers_and_surplus(
        branch=branch, transfers_dir=TRANSFERS_DIR,
        surplus_dir=REMAINING_SURPLUS_DIR, analytics_dir=ANALYTICS_DIR,
    )


def process_single_branch(branch: str, timestamp: str) -> tuple:
    """Process a single branch and return (merged_count, separate_count)."""
    logger.info(f"Processing branch: {branch}")
    
    from src.infrastructure.persistence.pandas_repository import PandasDataRepository
    from src.application.use_cases.combine_transfers import GenerateCombinedTransfers
    from src.domain.models.entities import Branch as BranchEntity
    
    # Use the enhanced repository directly
    repository = PandasDataRepository(
        input_dir="", 
        output_dir=TRANSFERS_DIR,
        surplus_dir=REMAINING_SURPLUS_DIR,
        analytics_dir=ANALYTICS_DIR
    )
    
    use_case = GenerateCombinedTransfers(repository, timestamp)
    return use_case.execute_for_branch(BranchEntity(name=branch))


def process_all_branches(timestamp: str) -> tuple:
    """Process all branches and return total counts."""
    total_merged = 0
    total_separate = 0
    for branch in get_branches():
        merged, separate = process_single_branch(branch, timestamp)
        total_merged += merged
        total_separate += separate
    return total_merged, total_separate
