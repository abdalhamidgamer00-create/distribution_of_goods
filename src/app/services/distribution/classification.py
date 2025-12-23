"""Service for classifying stock transfers into product categories."""

import os
from src.infrastructure.persistence.pandas_repository import PandasDataRepository
from src.application.use_cases.split_transfers import SplitTransfersByCategory
from src.shared.utils.logging_utils import get_logger
from src.application.interfaces.repository import DataRepository

logger = get_logger(__name__)

class TransferClassifier:
    """Manages the grouping of transfers by medical type (Creams, Syrups, etc.)."""

    def __init__(self, repository: DataRepository):
        self._repository = repository
        # specialized paths for transfer organization
        self._csv_dir = os.path.join("data", "output", "transfers", "csv")
        self._excel_dir = os.path.join("data", "output", "transfers", "excel")

    def execute(self, **kwargs) -> bool:
        """Splits raw transfers into categorized files for both CSV and Excel."""
        if not os.path.exists(self._csv_dir):
            logger.error(f"Transfers CSV directory not found: {self._csv_dir}")
            return False

        try:
            # specialized repository instance that focuses on the transfer directory
            repo = PandasDataRepository(
                input_dir="", 
                output_dir=self._csv_dir
            )
            
            use_case = SplitTransfersByCategory(
                repository=repo,
                excel_output_dir=self._excel_dir
            )
            
            success = use_case.execute()
            if success:
                logger.info("✓ Transfer classification completed successfully")
            return success
        except Exception as e:
            logger.exception(f"TransferClassifier failed: {e}")
            return False
