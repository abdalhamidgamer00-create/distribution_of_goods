"""Use case for orchestrating product distribution."""

from typing import List
from src.domain.models.distribution import DistributionResult
from src.domain.services.distribution_service import DistributionEngine
from src.application.interfaces.repository import DataRepository


class ProcessDistributions:
    """
    Application use case that orchestrates the distribution process.
    This follows the 'Clean Architecture' pattern where the use case
    coordinates domain entities and interfaces.
    """

    def __init__(
        self,
        repository: DataRepository,
        engine: DistributionEngine
    ):
        self._repository = repository
        self._engine = engine

    def execute(self) -> List[DistributionResult]:
        """
        Runs the full distribution process and persists transfers.
        """
        results = self.calculate()
        self.save(results)
        return results

    def calculate(self) -> List[DistributionResult]:
        """
        Calculates the distribution across all products and branches.
        """
        branches = self._repository.load_branches()
        products = self._repository.load_products()
        
        all_results = []
        
        # Pre-load all stock levels for all branches to avoid repeated IO
        branch_stocks_map = {
            branch.name: self._repository.load_stock_levels(branch)
            for branch in branches
        }
        
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
                # Store extra data for reporting
                result.branch_balances = branch_balances
                result.total_sales = total_sales
                all_results.append(result)
        
        return all_results

    def save(self, results: List[DistributionResult]) -> None:
        """Persists the generated transfers."""
        transfers = [t for res in results for t in res.transfers]
        self._repository.save_transfers(transfers)
