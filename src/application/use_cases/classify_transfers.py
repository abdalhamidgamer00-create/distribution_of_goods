"""Use case for classifying transfers into product categories."""

import os
from src.application.ports.repository import DataRepository
from src.shared.utility.logging_utils import get_logger

logger = get_logger(__name__)

class ClassifyTransfers:
    """
    Orchestrates the categorization of stock transfers.
    Loads raw transfers and saves them split by product category.
    """

    def __init__(self, repository: DataRepository):
        self._repository = repository
        self._excel_output_directory = os.path.join(
            "data", "output", "transfers", "excel"
        )

    def execute(self, **kwargs) -> bool:
        """
        Loads transfers from the repository and saves them split by category.
        """
        try:
            transfers_list = self._repository.load_transfers()
            if not transfers_list:
                logger.warning("No transfers found to classify.")
                return True
                
            logger.info("Classifying %d transfers by category...", len(transfers_list))
            
            # The repository handles the actual splitting and saving logic
            self._repository.save_split_transfers(
                transfers_list=transfers_list,
                excel_directory=self._excel_output_directory
            )
            
            logger.info("✓ Transfer classification completed successfully")
            return True
        except Exception as e:
            logger.exception(f"ClassifyTransfers use case failed: {e}")
            return False
