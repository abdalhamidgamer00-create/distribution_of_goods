"""Use case for reporting products with remaining surplus stock."""

from src.application.ports.repository import DataRepository
from src.application.use_cases.optimize_transfers import OptimizeTransfers
from src.shared.utility.logging_utils import get_logger

logger = get_logger(__name__)

class ReportSurplus:
    """
    Orchestrates the identification and reporting of excess inventory.
    Uses the distribution engine to calculate what remains after transfers.
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
        Calculates distributions and saves the remaining surplus report.
        """
        try:
            logger.info("Generating surplus reports...")
            # 1. Calculate all distribution results
            results = self._optimizer.calculate()
            
            # 2. Persist the surplus specific report
            self._repository.save_remaining_surplus(results)
            
            logger.info("✓ Surplus reporting completed successfully")
            return True
        except Exception as e:
            logger.exception(f"ReportSurplus use case failed: {e}")
            return False
