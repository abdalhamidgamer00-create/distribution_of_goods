"""Domain service for stock distribution logic."""

from typing import List, Dict, Tuple
from src.domain.models.entities import Product, Branch, StockLevel
from src.domain.models.distribution import Transfer, DistributionResult
from src.domain.services.priority_service import PriorityCalculator


from src.domain.services.distribution.metrics_service import DistributionMetricsService


class DistributionEngine:
    """Pure domain logic for distributing surplus to needing branches."""

    def __init__(self, priority_calculator: PriorityCalculator):
        self._calculator = priority_calculator
        self._metrics_service = DistributionMetricsService()

    def distribute_product(
        self, product: Product, needing_branches: list, surplus_branches: list
    ) -> DistributionResult:
        """Distribute surplus using a balanced multi-pass approach."""
        sorted_needs = sorted(
            needing_branches,
            key=lambda item: self._calculator.calculate_vulnerability_score(item[1]),
            reverse=True
        )
        surplus = {b.name: s.surplus for b, s in surplus_branches}
        needs = {c.name: s.needed for c, s in sorted_needs}
        matrix = {}
        
        while sum(surplus.values()) > 0 and sum(needs.values()) > 0:
            distributed = 0
            for consumer, _ in sorted_needs:
                if needs[consumer.name] > 0:
                    provider_name = max(surplus, key=surplus.get) if surplus else None
                    if provider_name and surplus[provider_name] > 0:
                        key = (provider_name, consumer.name)
                        matrix[key] = matrix.get(key, 0) + 1
                        surplus[provider_name] -= 1
                        needs[consumer.name] -= 1
                        distributed += 1
                if sum(surplus.values()) <= 0: break
            if distributed == 0: break
        
        all_branches = {b.name: b for b, s in needing_branches + surplus_branches}
        all_stocks = {b.name: s for b, s in needing_branches + surplus_branches}
        transfers = [
            Transfer(
                product=product, from_branch=all_branches[f], to_branch=all_branches[t],
                quantity=q, sender_balance=all_stocks[f].balance, receiver_balance=all_stocks[t].balance
            ) for (f, t), q in matrix.items() if q > 0
        ]
        return self._metrics_service.build_result(product, transfers, needing_branches, surplus)
