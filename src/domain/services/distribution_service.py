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
        self, product: Product, needing_branches: list, surplus_branches: list
    ) -> DistributionResult:
        """Distribute surplus using a balanced multi-pass approach."""
        sorted_needs = self._sort_needs_by_priority(needing_branches)
        surplus, needs, matrix = self._initialize_state(
            sorted_needs, surplus_branches
        )
        
        self._run_distribution_loop(
            sorted_needs, surplus_branches, surplus, needs, matrix
        )
        
        transfers = self._convert_matrix_to_transfers(
            product, matrix, needing_branches, surplus_branches
        )

        return self._build_distribution_result(
            product, transfers, needing_branches, surplus
        )

    def _initialize_state(self, sorted_needs, surplus_branches) -> Tuple:
        """Initialize tracking dictionaries for distribution."""
        available_surplus = {
            branch.name: stock.surplus for branch, stock in surplus_branches
        }
        current_needs = {
            consumer.name: stock.needed for consumer, stock in sorted_needs
        }
        return available_surplus, current_needs, {}

    def _run_distribution_loop(self, sorted_needs, sources, surplus, needs, matrix):
        """Orchestrate the round-robin distribution until exhaustion."""
        while sum(surplus.values()) > 0 and sum(needs.values()) > 0:
            units_distributed = self._process_round_robin_pass(
                sorted_needs, sources, surplus, needs, matrix
            )
            if units_distributed == 0:
                break

    def _process_round_robin_pass(self, needs_list, sources, surplus, needs, matrix):
        """Perform one pass across all needy branches, giving 1 unit each."""
        total_pass_distributed = 0
        for consumer, _ in needs_list:
            if needs[consumer.name] > 0:
                total_pass_distributed += self._allocate_unit_if_available(
                    consumer, sources, surplus, needs, matrix
                )
            if sum(surplus.values()) <= 0:
                break
        return total_pass_distributed

    def _allocate_unit_if_available(self, consumer, sources, surplus, needs, matrix):
        """Find the best source and allocate one unit to the consumer."""
        provider = self._get_best_surplus_provider(sources, surplus)
        if provider and surplus[provider.name] > 0:
            self._record_unit_transfer(provider, consumer, surplus, needs, matrix)
            return 1
        return 0

    def _get_best_surplus_provider(self, sources, surplus_map):
        """Identify the branch with the highest current surplus."""
        sorted_sources = sorted(
            sources, key=lambda x: surplus_map[x[0].name], reverse=True
        )
        return sorted_sources[0][0] if sorted_sources else None

    def _record_unit_transfer(self, provider, consumer, surplus, needs, matrix):
        """Update states and transfer matrix for a single unit allocation."""
        key = (provider.name, consumer.name)
        matrix[key] = matrix.get(key, 0) + 1
        surplus[provider.name] -= 1
        needs[consumer.name] -= 1

    def _convert_matrix_to_transfers(self, product, matrix, needs, sources):
        """Transform the consolidated matrix into Domain Transfer objects."""
        all_branches = {b.name: b for b, s in needs + sources}
        all_stocks = {b.name: s for b, s in needs + sources}
        transfers = []
        
        for (from_name, to_name), quantity in matrix.items():
            if quantity > 0:
                transfers.append(Transfer(
                    product=product,
                    from_branch=all_branches[from_name],
                    to_branch=all_branches[to_name],
                    quantity=quantity,
                    sender_balance=all_stocks[from_name].balance,
                    receiver_balance=all_stocks[to_name].balance
                ))
        return transfers

    def _sort_needs_by_priority(self, needing_branches):
        """Sorts needing branches by vulnerability score (descending)."""
        return sorted(
            needing_branches,
            key=lambda item: self._calculator.calculate_vulnerability_score(
                item[1]
            ),
            reverse=True
        )

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
