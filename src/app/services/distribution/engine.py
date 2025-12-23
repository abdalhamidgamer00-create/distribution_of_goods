"""Service for calculating and optimizing stock transfers between branches."""

import os
from src.infrastructure.persistence.pandas_repository import PandasDataRepository
from src.domain.services.distribution_service import DistributionEngine
from src.domain.services.priority_service import PriorityCalculator
from src.application.use_cases.process_distributions import ProcessDistributions
from src.shared.utils.logging_utils import get_logger
from src.application.interfaces.repository import DataRepository

logger = get_logger(__name__)

class TransferOptimizer:
    """Manages the logic for determining which products move between branches."""

    def __init__(self, repository: DataRepository):
        self._repository = repository
        self._stock_dir = os.path.join("data", "output", "branches", "analytics")
        self._transfer_dir = os.path.join("data", "output", "transfers", "csv")
        self._renamed_dir = os.path.join("data", "output", "converted", "renamed")

    def execute(self) -> bool:
        """Runs the distribution engine and saves the resulting transfer files."""
        if not os.path.exists(self._stock_dir):
            logger.error(f"Stock directory not found: {self._stock_dir}")
            return False

        try:
            # specialized repository for the distribution use case
            class UnifiedRepository(PandasDataRepository):
                def __init__(self, stock_dir, transfer_dir, renamed_dir):
                    super().__init__(input_dir=renamed_dir, output_dir=stock_dir)
                    self._transfer_dir = transfer_dir
                    
                def save_transfers(self, transfers):
                    old_output = self._output_dir
                    self._output_dir = self._transfer_dir
                    super().save_transfers(transfers)
                    self._output_dir = old_output

            repo = UnifiedRepository(
                stock_dir=self._stock_dir,
                transfer_dir=self._transfer_dir,
                renamed_dir=self._renamed_dir
            )
            
            if not repo.load_products():
                logger.error("No products found for distribution.")
                return False
                
            priority_calculator = PriorityCalculator()
            engine = DistributionEngine(priority_calculator)
            use_case = ProcessDistributions(repo, engine)
            
            use_case.execute()
            logger.info("✓ Transfer optimization completed successfully")
            return True
        except Exception as e:
            logger.exception(f"TransferOptimizer failed: {e}")
            # Ensure the backup traceback is logged for debugging
            import traceback
            traceback.print_exc()
            return False
