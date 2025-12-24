from typing import List, Tuple
from src.domain.models.entities import (
    Branch, Product, StockLevel, NetworkStockState
)
from src.domain.models.distribution import DistributionResult
from src.domain.services.distribution_service import DistributionEngine
from src.domain.services.priority_service import PriorityCalculator
from src.application.ports.repository import DataRepository
from src.domain.services.model_factory import DomainModelFactory
from src.shared.utility.logging_utils import get_logger

logger = get_logger(__name__)


class OptimizeTransfers:
    """Orchestrates the process of determining optimal stock movements."""

    def __init__(self, repository: DataRepository, engine=None):
        self._repository = repository
        self._engine = engine or DistributionEngine(PriorityCalculator())
        self._factory = DomainModelFactory()

    def execute(self, **kwargs) -> List[DistributionResult]:
        """Runs the distribution optimization process and persists transfers."""
        try:
            results = self.calculate()
            self.save(results)
            logger.info("✓ Transfer optimization completed successfully")
            return results
        except Exception as error:
            logger.exception(f"OptimizeTransfers execution failed: {error}")
            return []

    def calculate(self) -> List[DistributionResult]:
        """Performs parallel calculation for all products."""
        branches = self._repository.load_branches()
        products = self._repository.load_products()
        network_state = self._factory.create_network_state(
            branches, self._repository.load_stock_levels
        )
        stocks_map = {
            b.name: self._repository.load_stock_levels(b) for b in branches
        }
        
        return [
            result for product in products 
            if (result := self._process_single_product(
                product, branches, stocks_map, network_state
            ))
        ]

    def save(self, results: List[DistributionResult]) -> None:
        """Persists the generated transfers to the repository."""
        transfers = [
            transfer for result in results for transfer in result.transfers
        ]
        self._repository.save_transfers(transfers)

    def _process_single_product(
        self, product, branches, stocks_map, network_state
    ) -> DistributionResult:
        """Determines distribution for a single product across branches."""
        needs, surpluses, sales = self._collect_distribution_needs(
            product, branches, stocks_map
        )
        if not needs and not surpluses:
            return None
        result = self._engine.distribute_product(product, needs, surpluses)
        result.branch_balances = self._extract_product_balances(
            product.code, branches, network_state
        )
        result.total_sales = sales
        return result

    def _collect_distribution_needs(self, product, branches, stocks_map) -> tuple:
        """Collects needs, surpluses, and total sales for a product."""
        needs, surpluses, total_sales = [], [], 0.0
        for branch in branches:
            branch_stocks = stocks_map[branch.name]
            if product.code in branch_stocks:
                stock = branch_stocks[product.code]
                total_sales += stock.sales
                if stock.needed > 0:
                    needs.append((branch, stock))
                elif stock.surplus > 0:
                    surpluses.append((branch, stock))
        return needs, surpluses, total_sales

    def _extract_product_balances(
        self, product_code: str, branches: List[Branch], state: NetworkStockState
    ) -> dict:
        """Extracts branch balances for a specific product."""
        return {
            branch.name: state.get_balance(branch.name, product_code) 
            for branch in branches
        }
