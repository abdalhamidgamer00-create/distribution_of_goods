"""Service for calculating metrics and building distribution results."""

from typing import List, Dict
from src.domain.models.entities import Product
from src.domain.models.distribution import Transfer, DistributionResult

class DistributionMetricsService:
    """Calculates remaining needs and builds the final result object."""

    @staticmethod
    def build_result(
        product: Product, 
        transfers: List[Transfer], 
        original_needs: list, 
        available_surplus: Dict[str, int]
    ) -> DistributionResult:
        """Constructs the final distribution result with computed metrics."""
        fulfilled = {
            branch.name: sum(t.quantity for t in transfers if t.to_branch == branch)
            for branch, stock in original_needs
        }
        
        # Calculate remaining need (20d)
        remaining_needed = sum(
            max(0, stock.needed - fulfilled.get(branch.name, 0))
            for branch, stock in original_needs
        )
        
        # Calculate remaining shortage (30d) for reporting (Net Network Shortage)
        gross_shortage = sum(
            max(0, stock.shortage - fulfilled.get(branch.name, 0))
            for branch, stock in original_needs
        )
        unallocated_surplus = sum(available_surplus.values())
        remaining_shortage = max(0, gross_shortage - unallocated_surplus)

        return DistributionResult(
            product=product,
            transfers=transfers,
            remaining_needed=remaining_needed,
            remaining_shortage=remaining_shortage,
            remaining_surplus=unallocated_surplus,
            remaining_branch_surplus=available_surplus
        )
