"""Use case for reporting products with network-wide shortages."""

from src.application.ports.repository import DataRepository
from src.application.use_cases.optimize_transfers import OptimizeTransfers
from src.shared.utility.logging_utils import get_logger

logger = get_logger(__name__)

class ReportShortage:
    """
    Orchestrates the identification and reporting of inventory gaps.
    Uses the distribution engine to calculate net shortages across the network.
    """

    def __init__(
        self,
        repository: DataRepository,
        optimizer: OptimizeTransfers = None
    ):
        self._repository = repository
        # Reuse the optimization logic to get consistent results
        self._optimizer = optimizer or OptimizeTransfers(repository)

    def execute(self, **kwargs) -> bool:
        """
        Calculates distributions and saves the network-wide shortage report.
        """
        try:
            logger.info("Generating shortage reports...")
            # 1. Calculate all distribution results
            results = self._optimizer.calculate()
            
            # 2. Persist the shortage specific report
            self._repository.save_shortage_report(results)
            
            logger.info("✓ Shortage reporting completed successfully")
            return True
        except Exception as e:
            logger.exception(f"ReportShortage use case failed: {e}")
            return False
