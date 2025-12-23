"""Use case for splitting transfer files by product category."""

from typing import List
from src.application.interfaces.repository import DataRepository
from src.domain.models.distribution import Transfer


class SplitTransfersByCategory:
    """
    Orchestrates the process of taking consolidated transfer files
    and splitting them into category-specific files (Excel and CSV).
    """

    def __init__(self, repository: DataRepository, excel_output_dir: str):
        self._repository = repository
        self._excel_output_dir = excel_output_dir

    def execute(self) -> bool:
        """
        Loads existing transfers, classifies them, and saves split files.
        """
        # Load transfers (usually from Step 7 output)
        transfers = self._repository.load_transfers()
        
        if not transfers:
            return False
            
        # Save split transfers (CSV and Excel)
        self._repository.save_split_transfers(transfers, self._excel_output_dir)
        return True
