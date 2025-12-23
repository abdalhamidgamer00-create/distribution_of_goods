"""Service for reporting products with remaining surplus stock."""

import os
from src.infrastructure.persistence.pandas_repository import PandasDataRepository
from src.domain.services.distribution_service import DistributionEngine
from src.domain.services.priority_service import PriorityCalculator
from src.application.use_cases.process_distributions import ProcessDistributions
from src.shared.utils.logging_utils import get_logger
from src.application.interfaces.repository import DataRepository

logger = get_logger(__name__)

class SurplusReporter:
    """Manages the generation of reports for products with no local demand."""

    def __init__(self, repository: DataRepository):
        self._repository = repository
        self._stock_dir = os.path.join("data", "output", "branches", "analytics")
        self._surplus_dir = os.path.join("data", "output", "remaining_surplus")
        self._renamed_dir = os.path.join("data", "output", "converted", "renamed")

    def execute(self) -> bool:
        """Calculates and saves reports for remaining surplus across all branches."""
        if not os.path.exists(self._stock_dir):
            logger.error(f"Stock directory not found: {self._stock_dir}")
            return False

        try:
            repo = PandasDataRepository(
                input_dir=self._renamed_dir,
                output_dir=self._stock_dir,
                surplus_dir=self._surplus_dir
            )
            
            priority_calculator = PriorityCalculator()
            engine = DistributionEngine(priority_calculator)
            use_case = ProcessDistributions(repo, engine)
            
            results = use_case.calculate()
            repo.save_remaining_surplus(results)
            
            logger.info("✓ Surplus reporting completed successfully")
            return True
        except Exception as e:
            logger.exception(f"SurplusReporter failed: {e}")
            return False
