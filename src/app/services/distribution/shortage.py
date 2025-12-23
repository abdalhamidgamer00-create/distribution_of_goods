"""Service for reporting products with network-wide shortages."""

import os
from src.infrastructure.persistence.pandas_repository import PandasDataRepository
from src.domain.services.distribution_service import DistributionEngine
from src.domain.services.priority_service import PriorityCalculator
from src.application.use_cases.process_distributions import ProcessDistributions
from src.shared.utils.logging_utils import get_logger
from src.application.interfaces.repository import DataRepository

logger = get_logger(__name__)

class ShortageReporter:
    """Manages the generation of gap analysis reports for the entire network."""

    def __init__(self, repository: DataRepository):
        self._repository = repository
        self._stock_dir = os.path.join("data", "output", "branches", "analytics")
        self._shortage_dir = os.path.join("data", "output", "shortage")
        self._renamed_dir = os.path.join("data", "output", "converted", "renamed")

    def execute(self, **kwargs) -> bool:
        """Calculates and saves reports for net shortages across all branches."""
        if not os.path.exists(self._stock_dir):
            logger.error(f"Stock directory not found: {self._stock_dir}")
            return False

        try:
            repo = PandasDataRepository(
                input_dir=self._renamed_dir,
                output_dir=self._stock_dir,
                shortage_dir=self._shortage_dir
            )
            
            priority_calculator = PriorityCalculator()
            engine = DistributionEngine(priority_calculator)
            use_case = ProcessDistributions(repo, engine)
            
            results = use_case.calculate()
            repo.save_shortage_report(results)
            
            logger.info("✓ Shortage reporting completed successfully")
            return True
        except Exception as e:
            logger.exception(f"ShortageReporter failed: {e}")
            return False
