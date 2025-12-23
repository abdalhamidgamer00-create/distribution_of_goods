"""Use case for segmenting global inventory data into branch-specific datasets."""

from typing import List
from src.domain.services.branch_service import BranchSplitter
from src.application.interfaces.repository import DataRepository
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

class SegmentBranches:
    """
    Orchestrates the process of splitting consolidated global data into
    branch-specific records and persisting them.
    """

    def __init__(
        self,
        repository: DataRepository,
        splitter: BranchSplitter = None
    ):
        self._repository = repository
        self._splitter = splitter or BranchSplitter()

    def execute(self, **kwargs) -> bool:
        """
        Loads consolidated data, splits it, and persists the results.
        """
        try:
            branches = self._repository.load_branches()
            consolidated_data = self._repository.load_consolidated_stock()
            
            if not consolidated_data:
                logger.error("No consolidated data found to segment.")
                return False
                
            logger.info("Segmenting data for %d branches...", len(branches))
            
            split_results = self._splitter.split_by_branch(
                consolidated_data, branches
            )
            
            for branch in branches:
                if branch.name in split_results:
                    self._repository.save_branch_stocks(
                        branch, split_results[branch.name]
                    )
            
            logger.info("✓ Data segmentation completed successfully")
            return True
        except Exception as e:
            logger.exception(f"SegmentBranches use case failed: {e}")
            return False
