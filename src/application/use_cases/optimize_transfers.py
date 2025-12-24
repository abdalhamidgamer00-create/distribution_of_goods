"""Use case for calculating and optimizing stock transfers."""

from typing import List
from src.domain.models.distribution import DistributionResult
from src.domain.services.distribution_service import DistributionEngine
from src.domain.services.priority_service import PriorityCalculator
from src.application.interfaces.repository import DataRepository
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


class OptimizeTransfers:
    """Orchestrates the process of determining optimal stock movements."""

    def __init__(self, repository: DataRepository, engine: DistributionEngine = None):
        self._repository = repository
        self._engine = engine or DistributionEngine(PriorityCalculator())

    def execute(self, **kwargs) -> List[DistributionResult]:
        """Runs the distribution optimization process and persists transfers."""
        try:
            results = self.calculate()
            self.save(results)
            logger.info("✓ Transfer optimization completed successfully")
            return results
        except Exception as error:
            logger.exception(f"OptimizeTransfers use case failed: {error}")
            return []

    def calculate(self) -> List[DistributionResult]:
        """Performs calculation for all products across all branches."""
        branches = self._repository.load_branches()
        products = self._repository.load_products()
        logger.info("OptimizeTransfers: Calculating for %d branches.", len(branches))
        
        branch_stocks_map = self._load_all_branch_stocks(branches)
        all_results = []
        
        for product in products:
            result = self._process_single_product(product, branches, branch_stocks_map)
            if result:
                all_results.append(result)
        
        return all_results

    def save(self, results: List[DistributionResult]) -> None:
        """Persists the generated transfers to the repository."""
        transfers = [t for res in results for t in res.transfers]
        logger.info("OptimizeTransfers: Saving %d transfers.", len(transfers))
        self._repository.save_transfers(transfers)

    def _load_all_branch_stocks(self, branches: list) -> dict:
        """Loads and maps stock levels for all branches."""
        stocks_map = {}
        for branch in branches:
            stocks_map[branch.name] = self._repository.load_stock_levels(branch)
        return stocks_map

    def _process_single_product(self, product, branches, stocks_map) -> DistributionResult:
        """Determines distribution for a single product across branches."""
        needs, surpluses, balances, sales = self._collect_product_context(
            product, branches, stocks_map
        )
        
        if not needs and not surpluses:
            return None
            
        result = self._engine.distribute_product(product, needs, surpluses)
        result.branch_balances = balances
        result.total_sales = sales
        return result

    def _collect_product_context(self, product, branches, stocks_map) -> tuple:
        """Collects needs, surpluses, and balances for a product."""
        needs = []
        surpluses = []
        balances = {}
        total_sales = 0.0
        
        for branch in branches:
            branch_stocks = stocks_map[branch.name]
            if product.code in branch_stocks:
                stock = branch_stocks[product.code]
                balances[branch.name] = stock.balance
                total_sales += stock.sales
                
                if stock.needed > 0:
                    needs.append((branch, stock))
                elif stock.surplus > 0:
                    surpluses.append((branch, stock))
                    
        return needs, surpluses, balances, total_sales
