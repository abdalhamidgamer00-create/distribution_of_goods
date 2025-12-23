"""Service for consolidating transfers and surplus into final logistics reports."""

from datetime import datetime
from src.core.domain.branches.config import get_branches
from src.shared.utils.logging_utils import get_logger
from src.infrastructure.persistence.pandas_repository import PandasDataRepository
from src.application.use_cases.combine_transfers import GenerateCombinedTransfers
from src.domain.models.entities import Branch as BranchEntity
from src.application.interfaces.repository import DataRepository
from src.app.pipeline.step_11.runner.constants import (
    TRANSFERS_DIR,
    REMAINING_SURPLUS_DIR,
    ANALYTICS_DIR,
)

logger = get_logger(__name__)

class ConsolidationService:
    """Manages the creation of final merged and separate logistics reports."""

    def __init__(self, repository: DataRepository):
        self._repository = repository

    def execute(self) -> bool:
        """Processes all branches to generate consolidated logistics files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # specialized repository for consolidation
            repo = PandasDataRepository(
                input_dir="", 
                output_dir=TRANSFERS_DIR,
                surplus_dir=REMAINING_SURPLUS_DIR,
                analytics_dir=ANALYTICS_DIR
            )
            
            use_case = GenerateCombinedTransfers(repo, timestamp)
            
            total_merged = 0
            total_separate = 0
            
            for branch_name in get_branches():
                logger.info(f"Processing branch: {branch_name}")
                merged, separate = use_case.execute_for_branch(BranchEntity(name=branch_name))
                total_merged += merged
                total_separate += separate
            
            self._log_summary(total_merged, total_separate)
            return (total_merged + total_separate) > 0
            
        except Exception as e:
            logger.exception(f"ConsolidationService failed: {e}")
            return False

    def _log_summary(self, merged_count: int, separate_count: int) -> None:
        """Logs a summary of the generation process."""
        logger.info("=" * 50)
        logger.info(f"Generated {merged_count} merged files (CSV + Excel)")
        logger.info(f"Generated {separate_count} separate files (CSV + Excel)")
        logger.info(f"Merged output: data/output/combined_transfers/merged/excel")
        logger.info(f"Separate output: data/output/combined_transfers/separate/excel")
