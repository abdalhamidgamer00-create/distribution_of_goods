"""Use case for segmenting global inventory data\ninto branch-specific datasets."""

from typing import Dict, List
from src.domain.services.branch_service import BranchSplitter
from src.application.ports.repository import DataRepository
from src.shared.utility.logging_utils import get_logger

logger = get_logger(__name__)


class SegmentBranches:
    """Orchestrates splitting consolidated data\ninto branch-specific records."""

    def __init__(
        self,
        repository: DataRepository,
        splitter: BranchSplitter = None
    ):
        self._repository = repository
        self._splitter = splitter or BranchSplitter()

    def execute(self, **kwargs) -> bool:
        """Loads consolidated data, splits it, and persists the results."""
        try:
            branches = self._repository.load_branches()
            data = self._repository.load_consolidated_stock()
            
            if not data:
                logger.error("No consolidated data found to segment.")
                return False
                
            logger.info("Segmenting data for %d branches...", len(branches))
            split_results = self._splitter.split_by_branch(data, branches)
            
            self._save_segmented_branches(branches, split_results)
            logger.info("✓ Data segmentation completed successfully")
            return True
        except Exception as error:
            logger.exception(f"SegmentBranches use case failed: {error}")
            return False

    def _save_segmented_branches(self, branches, results_map: Dict) -> None:
        """Iterates through branches and saves their respective stock data."""
        for branch in branches:
            if branch.name in results_map:
                self._repository.save_branch_stocks(
                    branch, results_map[branch.name]
                )
