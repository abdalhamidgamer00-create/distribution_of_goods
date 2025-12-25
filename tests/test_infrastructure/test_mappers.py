"""Tests for the StockMapper."""

import pytest
import pandas as pd
from src.infrastructure.repositories.mappers.mappers import StockMapper


class TestStockMapper:
    
    def test_to_consolidated_stock_calculates_quantities_correctly(self):
        # Arrange
        row = pd.Series({
            'code': 'P1',
            'product_name': 'Product 1',
            'asherin_sales': 90.0,
            'asherin_balance': 50.0,
            'wardani_sales': 0.0,
            'wardani_balance': 100.0,
            # ... and so on for all branches, but StockMapper uses BRANCHES constant
        })
        # Add missing columns
        from src.shared.constants import BRANCHES
        for b in BRANCHES:
            if f"{b}_sales" not in row:
                row[f"{b}_sales"] = 0.0
            if f"{b}_balance" not in row:
                row[f"{b}_balance"] = 0.0
        
        num_days = 90
        
        # Act
        result = StockMapper.to_consolidated_stock(row, num_days)
        
        # Assert
        # asherin: 90 sales / 90 days = 1.0 avg_sales
        # coverage_qty = ceil(1.0 * 20) = 20
        # balance = 50. Surplus = 50 - 20 = 30. Needed = 0.
        asherin_stock = result.branch_stocks['asherin']
        assert asherin_stock.avg_sales == 1.0
        assert asherin_stock.surplus == 30
        assert asherin_stock.needed == 0
        
        # wardani: 0 sales. monthly_qty = 0. balance = 100. Surplus = 100. Needed = 0.
        wardani_stock = result.branch_stocks['wardani']
        assert wardani_stock.avg_sales == 0.0
        assert wardani_stock.surplus == 100
        assert wardani_stock.needed == 0

    def test_to_consolidated_stock_handles_needed_quantity(self):
        # Arrange
        row = pd.Series({
            'code': 'P2',
            'product_name': 'Product 2',
            'asherin_sales': 180.0,
            'asherin_balance': 20.0,
        })
        from src.shared.constants import BRANCHES
        for b in BRANCHES:
            if f"{b}_sales" not in row:
                row[f"{b}_sales"] = 0.0
            if f"{b}_balance" not in row:
                row[f"{b}_balance"] = 0.0
                
        num_days = 90
        
        # Act
        result = StockMapper.to_consolidated_stock(row, num_days)
        
        # Assert
        # asherin: 180 sales / 90 days = 2.0 avg_sales
        # coverage_qty = ceil(2.0 * 20) = 40
        # balance = 20. Surplus = 0.
        # Raw Needed = 40 - 20 = 20.
        # Capped Needed = min(20, 30 - 20) = 10.
        asherin_stock = result.branch_stocks['asherin']
        assert asherin_stock.avg_sales == 2.0
        assert asherin_stock.surplus == 0
        assert asherin_stock.needed == 10
