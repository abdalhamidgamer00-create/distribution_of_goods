"""Domain service for priority calculations."""

from src.domain.models.entities import StockLevel
from src.shared.constants import PRIORITY_WEIGHTS


class PriorityCalculator:
    """Calculates priority scores based on weighted business rules."""

    @staticmethod
    def calculate_vulnerability_score(stock: StockLevel) -> float:
        """
        Calculate how much a branch needs a product.
        Higher score = higher priority.
        """
        if stock.needed <= 0:
            return 0.0
            
        # Avoid division by zero, 0.1 is a smoothing factor
        inverse_balance_score = 1.0 / (stock.balance + 0.1)
        
        weights = PRIORITY_WEIGHTS
        return (
            weights["balance"] * inverse_balance_score +
            weights["needed"] * stock.needed +
            weights["avg_sales"] * stock.avg_sales
        )

    @staticmethod
    def calculate_surplus_rank(stock: StockLevel) -> float:
        """
        Calculate ranking for surplus sources.
        We prefer branches with more surplus and better balance.
        """
        # Secondary ranking factors: balance and avg_sales
        # This mirrors the logic in get_surplus_sources_ordered_for_product
        return stock.surplus
