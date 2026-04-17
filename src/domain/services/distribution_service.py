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
        """Distribute surplus to needing branches using balanced Round-Robin."""
        sorted_needs = self._sort_needs_by_priority(needing_branches)
        
        # Track available surplus per branch
        available_surplus = {
            branch.name: stock.surplus 
            for branch, stock in surplus_branches
        }
        
        # Track remaining need per consumer branch
        current_needs = {
            consumer.name: stock.needed
            for consumer, stock in sorted_needs
        }
        
        # Matrix to hold consolidated transfers: (from_name, to_name) -> quantity
        transfer_matrix = {}

        # Round-Robin Distribution: 1 unit per branch per pass
        while sum(available_surplus.values()) > 0 and sum(current_needs.values()) > 0:
            any_distributed = False
            
            for consumer_branch, consumer_stock in sorted_needs:
                if current_needs[consumer_branch.name] <= 0:
                    continue
                
                # Find best surplus source (branch with most surplus)
                sorted_sources = sorted(
                    surplus_branches,
                    key=lambda x: available_surplus[x[0].name],
                    reverse=True
                )
                
                provider, provider_stock = sorted_sources[0]
                if available_surplus[provider.name] > 0:
                    # Distribute 1 unit
                    qty = 1
                    key = (provider.name, consumer_branch.name)
                    transfer_matrix[key] = transfer_matrix.get(key, 0) + qty
                    
                    available_surplus[provider.name] -= qty
                    current_needs[consumer_branch.name] -= qty
                    any_distributed = True
                    
                    if sum(available_surplus.values()) <= 0:
                        break
            
            if not any_distributed:
                break

        # Convert matrix back to Transfer objects
        transfers = []
        # Create lookup for branch objects
        all_branches = {b.name: b for b, s in needing_branches + surplus_branches}
        all_stocks = {b.name: s for b, s in needing_branches + surplus_branches}
        
        for (from_name, to_name), qty in transfer_matrix.items():
            if qty > 0:
                transfers.append(Transfer(
                    product=product,
                    from_branch=all_branches[from_name],
                    to_branch=all_branches[to_name],
                    quantity=qty,
                    sender_balance=all_stocks[from_name].balance,
                    receiver_balance=all_stocks[to_name].balance
                ))

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
        self, product, consumer, consumer_stock, 
        surplus_branches, available_surplus
    ) -> List[Transfer]:
        """Fulfill single branch's need from surplus sources."""
        transfers = []
        remaining_needed = consumer_stock.needed
        sorted_sources = sorted(
            surplus_branches,
            key=lambda item: available_surplus[item[0].name],
            reverse=True
        )
        for provider_branch, provider_stock in sorted_sources:
            if remaining_needed <= 0:
                break
            qty = self._calculate_transfer_quantity(
                remaining_needed, available_surplus[provider_branch.name]
            )
            if qty > 0:
                transfers.append(Transfer(
                    product=product, from_branch=provider_branch, 
                    to_branch=consumer, quantity=qty,
                    sender_balance=provider_stock.balance,
                    receiver_balance=consumer_stock.balance
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
