"""Domain service for calculating stock requirements and surpluses."""

import math
from src.domain.models.entities import StockLevel


class StockCalculator:
    """Handles core inventory calculations for distribution logic."""

    @staticmethod
    def calculate_stock_level(
        sales_quantity: float,
        balance_quantity: float,
        days_covered: int
    ) -> StockLevel:
        """
        Calculates inventory needs and surpluses for a branch.
        
        Args:
            sales_quantity: Total sales during the period
            balance_quantity: Current branch balance
            days_covered: Number of days in the sales period
            
        Returns:
            StockLevel: Domain model containing calculated metrics
        """
        daily_average_sales = (
            sales_quantity / days_covered if days_covered > 0 else 0.0
        )
        monthly_inventory_need = math.ceil(daily_average_sales * 30)
        
        surplus_quantity = math.floor(
            max(0, balance_quantity - monthly_inventory_need)
        )
        needed_quantity = math.ceil(
            max(0, monthly_inventory_need - balance_quantity)
        )
        
        return StockLevel(
            needed=needed_quantity,
            surplus=surplus_quantity,
            balance=float(balance_quantity),
            avg_sales=float(daily_average_sales),
            sales=float(sales_quantity)
        )
