"""Domain service for stock distribution logic."""

from typing import List, Dict, Tuple
from src.domain.models.entities import Product, Branch, StockLevel
from src.domain.models.distribution import Transfer, DistributionResult
from src.domain.services.priority_service import PriorityCalculator


class DistributionEngine:
    """Pure domain logic for distributing surplus to needing branches."""

    def __init__(self, priority_calculator: PriorityCalculator):
        self._calculator = priority_calculator

    def distribute_product(
        self, product, needing_branches, surplus_branches
    ) -> DistributionResult:
        """Distribute surplus to needing branches based on priority."""
        sorted_needs = self._sort_needs_by_priority(needing_branches)
        available_surplus = {
            branch.name: stock.surplus 
            for branch, stock in surplus_branches
        }
        transfers = []
        for consumer_branch, consumer_stock in sorted_needs:
            branch_transfers = self._fulfill_branch_need(
                product, consumer_branch, consumer_stock.needed, 
                surplus_branches, available_surplus
            )
            transfers.extend(branch_transfers)
        return self._build_distribution_result(
            product, transfers, needing_branches, available_surplus
        )

    def _sort_needs_by_priority(self, needing_branches):
        """Sorts needing branches by vulnerability score (descending)."""
        return sorted(
            needing_branches,
            key=lambda item: self._calculator.calculate_vulnerability_score(
                item[1]
            ),
            reverse=True
        )

    def _fulfill_branch_need(
        self, product, consumer, needed_amount, 
        surplus_branches, available_surplus
    ) -> List[Transfer]:
        """Fulfill single branch's need from surplus sources."""
        transfers = []
        remaining_needed = needed_amount
        sorted_sources = sorted(
            surplus_branches,
            key=lambda item: available_surplus[item[0].name],
            reverse=True
        )
        for provider_branch, _ in sorted_sources:
            if remaining_needed <= 0:
                break
            qty = self._calculate_transfer_quantity(
                remaining_needed, available_surplus[provider_branch.name]
            )
            if qty > 0:
                transfers.append(Transfer(
                    product=product, from_branch=provider_branch, 
                    to_branch=consumer, quantity=qty
                ))
                available_surplus[provider_branch.name] -= qty
                remaining_needed -= qty
        return transfers

    def _calculate_transfer_quantity(self, needed: int, available: int) -> int:
        """Calculates the maximum possible transfer quantity."""
        return min(needed, max(0, available))

    def _build_distribution_result(
        self, product, transfers, original_needs, available_surplus
    ) -> DistributionResult:
        """Constructs the final distribution result with metrics."""
        fulfilled = {
            b.name: sum(t.quantity for t in transfers if t.to_branch == b)
            for b, s in original_needs
        }
        remaining_needed = sum(
            max(0, s.needed - fulfilled.get(b.name, 0))
            for b, s in original_needs
        )
        return DistributionResult(
            product=product, transfers=transfers,
            remaining_needed=remaining_needed,
            remaining_surplus=sum(available_surplus.values()),
            remaining_branch_surplus=available_surplus
        )
