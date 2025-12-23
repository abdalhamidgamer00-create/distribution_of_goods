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
        self,
        product: Product,
        needing_branches: List[Tuple[Branch, StockLevel]],
        surplus_branches: List[Tuple[Branch, StockLevel]]
    ) -> DistributionResult:
        """
        Distribute available surplus to needing branches based on priority.
        """
        # Sort needing branches by vulnerability (highest score first)
        sorted_needs = sorted(
            needing_branches,
            key=lambda item: self._calculator.calculate_vulnerability_score(item[1]),
            reverse=True
        )

        transfers = []
        # Create a mutable copy of surplus stocks
        available_surplus = {b.name: s.surplus for b, s in surplus_branches}
        surplus_entities = {b.name: b for b, _ in surplus_branches}
        
        total_remaining_needed = sum(s.needed for _, s in needing_branches)
        
        for consumer, consumer_stock in sorted_needs:
            needed_amount = consumer_stock.needed
            
            # Find best surplus sources for this consumer
            # Sort surplus sources: more surplus first
            potential_sources = sorted(
                surplus_branches,
                key=lambda item: available_surplus[item[0].name],
                reverse=True
            )

            for provider, _ in potential_sources:
                if needed_amount <= 0:
                    break
                    
                provider_name = provider.name
                if available_surplus[provider_name] <= 0:
                    continue
                    
                # Calculate how much to transfer
                transfer_qty = min(needed_amount, available_surplus[provider_name])
                
                transfers.append(Transfer(
                    product=product,
                    from_branch=provider,
                    to_branch=consumer,
                    quantity=transfer_qty
                ))
                
                available_surplus[provider_name] -= transfer_qty
                needed_amount -= transfer_qty
                total_remaining_needed -= transfer_qty

        total_remaining_surplus = sum(available_surplus.values())

        return DistributionResult(
            product=product,
            transfers=transfers,
            remaining_needed=total_remaining_needed,
            remaining_surplus=total_remaining_surplus,
            remaining_branch_surplus=available_surplus
        )
