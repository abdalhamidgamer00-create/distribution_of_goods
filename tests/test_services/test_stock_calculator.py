import pytest
from src.domain.services.inventory.stock_calculator import StockCalculator
from src.domain.models.config import InventoryConfig
from src.domain.models.entities import StockLevel

def test_calculate_stock_level_with_defaults():
    # Default: Need=20, Surplus=60, Shortage=30
    # Sales=100, Days=10 -> DailyAvg=10
    # NeedTarget=200, SurplusTarget=600, ShortageTarget=300
    
    # Case 1: Low balance (10) -> Need = NeedTarget - Balance
    # NeedTarget = 10 * 20 = 200. RawNeed = 200 - 10 = 190.
    result = StockCalculator.calculate_stock_level(
        sales_quantity=100,
        balance_quantity=10,
        days_covered=10
    )
    
    assert result.average_daily_sales == 10.0
    assert result.needed == 20  # Capped by MAX_BALANCE_FOR_NEED_THRESHOLD (30 - 10)
    assert result.shortage == 290 # 300 - 10 = 290
    assert result.surplus == 0

def test_calculate_stock_level_with_custom_config():
    # Custom: Need=10, Surplus=20, Shortage=5
    config = InventoryConfig(need_days=10, surplus_days=20, shortage_days=5)
    
    # Sales=100, Days=10 -> DailyAvg=10
    # NeedTarget=100, SurplusTarget=200, ShortageTarget=50
    
    # Case 2: Balance 150
    result = StockCalculator.calculate_stock_level(
        sales_quantity=100,
        balance_quantity=150,
        days_covered=10,
        config=config
    )
    
    assert result.average_daily_sales == 10.0
    assert result.needed == 0 # Balance 150 > NeedTarget 100
    assert result.shortage == 0 # Balance 150 > ShortageTarget 50
    assert result.surplus == 0 # Balance 150 < SurplusTarget 200
    
    # Case 3: Balance 250 -> Surplus
    result_surplus = StockCalculator.calculate_stock_level(
        sales_quantity=100,
        balance_quantity=250,
        days_covered=10,
        config=config
    )
    assert result_surplus.surplus == 50 # 250 - 200 = 50

def test_zero_days_covered():
    result = StockCalculator.calculate_stock_level(
        sales_quantity=100,
        balance_quantity=50,
        days_covered=0
    )
    assert result.average_daily_sales == 0.0
    assert result.needed == 0
    assert result.surplus == 50 # floor(max(0, 50 - 0))
