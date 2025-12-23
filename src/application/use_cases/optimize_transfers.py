"""Use case for calculating and optimizing stock transfers between branches."""

from typing import List
from src.domain.models.distribution import DistributionResult
from src.domain.services.distribution_service import DistributionEngine
from src.domain.services.priority_service import PriorityCalculator
from src.application.interfaces.repository import DataRepository
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)

class OptimizeTransfers:
    """
    Orchestrates the process of determining optimal stock movements.
    Coordinates domain entities, priority calculation, and data persistence.
    """

    def __init__(
        self,
        repository: DataRepository,
        engine: DistributionEngine = None
    ):
        self._repository = repository
        # Initialize engine with default priority calculator if not provided
        self._engine = engine or DistributionEngine(PriorityCalculator())

    def execute(self, **kwargs) -> List[DistributionResult]:
        """
        Runs the full distribution optimization process and persists transfers.
        """
        try:
            results = self.calculate()
            self.save(results)
            logger.info("✓ Transfer optimization completed successfully")
            return results
        except Exception as e:
            logger.exception(f"OptimizeTransfers use case failed: {e}")
            return []

    def calculate(self) -> List[DistributionResult]:
        """
        Performs the distribution calculation for all products across all branches.
        """
        branches = self._repository.load_branches()
        products = self._repository.load_products()
        
        logger.info("OptimizeTransfers: Calculating for %d branches and %d products.", len(branches), len(products))
        
        all_results = []
        
        # Pre-load all stock levels for all branches to optimize IO
        branch_stocks_map = {}
        for branch in branches:
            stocks = self._repository.load_stock_levels(branch)
            branch_stocks_map[branch.name] = stocks
        
        for product in products:
            needing_branches = []
            surplus_branches = []
            branch_balances = {}
            total_sales = 0.0
            
            for branch in branches:
                stocks = branch_stocks_map[branch.name]
                if product.code in stocks:
                    stock = stocks[product.code]
                    branch_balances[branch.name] = stock.balance
                    total_sales += stock.sales
                    
                    if stock.needed > 0:
                        needing_branches.append((branch, stock))
                    elif stock.surplus > 0:
                        surplus_branches.append((branch, stock))
            
            if needing_branches or surplus_branches:
                result = self._engine.distribute_product(
                    product, needing_branches, surplus_branches
                )
                # Store extra metadata for reporting layers
                result.branch_balances = branch_balances
                result.total_sales = total_sales
                all_results.append(result)
        
        return all_results

    def save(self, results: List[DistributionResult]) -> None:
        """Persists the generated transfers to the repository."""
        all_transfers = [transfer for result in results for transfer in result.transfers]
        logger.info("OptimizeTransfers: Saving %d transfers.", len(all_transfers))
        self._repository.save_transfers(all_transfers)
