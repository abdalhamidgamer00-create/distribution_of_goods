"""Domain service for calculating stock requirements and surpluses."""

import math
from src.domain.models.entities import StockLevel
from src.shared.constants import (
    STOCK_COVERAGE_DAYS, 
    MAX_BALANCE_FOR_NEED_THRESHOLD,
    MIN_COVERAGE_FOR_SMALL_NEED_SUPPRESSION,
    MIN_NEED_THRESHOLD
)


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
        target_inventory_coverage = math.ceil(
            daily_average_sales * STOCK_COVERAGE_DAYS
        )
        
        surplus_quantity = math.floor(
            max(0, balance_quantity - target_inventory_coverage)
        )
        needed_quantity = math.ceil(
            max(0, target_inventory_coverage - balance_quantity)
        )
        
        # New Rule: If balance >= threshold, suppress need to 0
        if balance_quantity >= MAX_BALANCE_FOR_NEED_THRESHOLD:
            needed_quantity = 0
            
        # New Rule: Small Need Suppression
        # If coverage >= 15 and need < 10, suppress to 0
        if (target_inventory_coverage >= MIN_COVERAGE_FOR_SMALL_NEED_SUPPRESSION 
            and needed_quantity < MIN_NEED_THRESHOLD):
            needed_quantity = 0
            
        # New Rule: Max Balance Capping
        # Ensure that (balance + need) <= MAX_BALANCE_FOR_NEED_THRESHOLD
        if needed_quantity > 0:
            available_space = max(0, MAX_BALANCE_FOR_NEED_THRESHOLD - balance_quantity)
            needed_quantity = min(needed_quantity, int(available_space))

        return StockLevel(
            needed=needed_quantity,
            surplus=surplus_quantity,
            balance=float(balance_quantity),
            avg_sales=float(daily_average_sales),
            sales=float(sales_quantity)
        )
