"""Service for segmenting global inventory data into branch-specific datasets."""

import os
from src.infrastructure.persistence.pandas_repository import PandasDataRepository
from src.domain.services.branch_service import BranchSplitter
from src.application.use_cases.branch_split import SplitDataByBranch
from src.shared.utils.logging_utils import get_logger
from src.application.interfaces.repository import DataRepository

logger = get_logger(__name__)

class SegmentationService:
    """Manages the partitioning of normalized data for individual branches."""

    def __init__(self, repository: DataRepository):
        self._repository = repository
        # Segmentation uses specific input and target locations
        self._input_dir = os.path.join("data", "output", "converted", "renamed")
        self._analytics_dir = os.path.join("data", "output", "branches", "analytics")
        self._files_dir = os.path.join("data", "output", "branches", "files")

    def execute(self) -> bool:
        """Splits the normalized CSV into branch-specific analytics and user files."""
        if not os.path.exists(self._input_dir):
            logger.error(f"Input directory not found: {self._input_dir}")
            return False

        try:
            # We use specialized repository instances for the split use case
            # to preserve backward compatibility with existing path structures
            repo_analytics = PandasDataRepository(
                input_dir=self._input_dir,
                output_dir=self._analytics_dir
            )
            
            splitter = BranchSplitter()
            use_case = SplitDataByBranch(repo_analytics, splitter)
            
            # Verify data exists
            if not repo_analytics.load_products():
                logger.error("No products found to segment. Check normalization output.")
                return False
                
            use_case.execute()
            
            # Also populate the 'files' directory for legacy compatibility
            repo_files = PandasDataRepository(
                input_dir=self._input_dir,
                output_dir=self._files_dir
            )
            SplitDataByBranch(repo_files, splitter).execute()
            
            logger.info("✓ Data segmentation completed successfully")
            return True
        except Exception as e:
            logger.exception(f"SegmentationService failed: {e}")
            return False
