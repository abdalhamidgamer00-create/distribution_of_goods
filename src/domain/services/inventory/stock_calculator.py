"""Domain service for calculating stock requirements and surpluses."""

import math
from src.domain.models.entities import StockLevel
from src.domain.models.config import InventoryConfig
from src.shared.constants import (
    NEED_COVERAGE_DAYS, SURPLUS_COVERAGE_DAYS, SHORTAGE_COVERAGE_DAYS
)
from .inventory_rules import apply_scalar_rules


class StockCalculator:
    """Handles multi-target inventory calculations."""

    @staticmethod
    def calculate_stock_level(
        sales_quantity: float,
        balance_quantity: float,
        days_covered: int,
        config: InventoryConfig = None
    ) -> StockLevel:
        """Calculates surplus, needs and shortage based on config or defaults."""
        config = config or InventoryConfig.default()
        daily_average_sales = (
            sales_quantity / days_covered if days_covered > 0 else 0.0
        )
        
        # 1. Targets for different contexts
        surplus_target = math.ceil(daily_average_sales * config.surplus_days)
        need_target = math.ceil(daily_average_sales * config.need_days)
        shortage_target = math.ceil(daily_average_sales * config.shortage_days)

        # 2. Raw quantities
        surplus_quantity = math.floor(max(0, balance_quantity - surplus_target))
        needed_quantity = math.ceil(max(0, need_target - balance_quantity))
        shortage_quantity = math.ceil(max(0, shortage_target - balance_quantity))
        
        # 3. Apply business rules to the 'need' (for transfers)
        needed_quantity = apply_scalar_rules(
            needed=needed_quantity,
            balance=balance_quantity,
            coverage=need_target
        )

        return StockLevel(
            needed=needed_quantity,
            surplus=surplus_quantity,
            balance=float(balance_quantity),
            average_daily_sales=float(daily_average_sales),
            sales=float(sales_quantity),
            shortage=shortage_quantity
        )
