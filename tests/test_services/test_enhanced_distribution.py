"""Tests for enhanced distribution logic, including balances and avg_sales recalculation."""

import pytest
from datetime import datetime
from src.domain.models.entities import Product, Branch, StockLevel
from src.domain.models.distribution import Transfer
from src.domain.services.inventory.stock_calculator import StockCalculator
from src.domain.services.validation.dates import (
    calculate_days_between, get_sheet_duration_days
)
from src.infrastructure.repositories.mappers.mappers import StockMapper
import pandas as pd
import os

def test_transfer_model_includes_balances():
    """Verify that Transfer model correctly stores sender and receiver balances."""
    product = Product(code="123", name="Test Product")
    from_branch = Branch(name="Source")
    to_branch = Branch(name="Target")
    
    transfer = Transfer(
        product=product,
        from_branch=from_branch,
        to_branch=to_branch,
        quantity=10,
        sender_balance=50.0,
        receiver_balance=5.0
    )
    
    assert transfer.sender_balance == 50.0
    assert transfer.receiver_balance == 5.0
    assert transfer.quantity == 10

def test_stock_calculator_recalculates_avg_sales():
    """Verify that StockCalculator calculates avg_sales correctly based on days."""
    sales = 90.0
    balance = 100.0
    days = 90
    
    # Standard 90 days
    stock_90 = StockCalculator.calculate_stock_level(sales, balance, days)
    assert stock_90.avg_sales == 1.0
    
    # Custom 45 days
    stock_45 = StockCalculator.calculate_stock_level(sales, balance, 45)
    assert stock_45.avg_sales == 2.0
    
    # Custom 10 days
    stock_10 = StockCalculator.calculate_stock_level(sales, balance, 10)
    assert stock_10.avg_sales == 9.0

def test_dates_calculate_days_between():
    """Verify date difference calculation."""
    start = datetime(2025, 1, 1, 0, 0)
    end = datetime(2025, 1, 11, 0, 0) # 10 days
    
    days = calculate_days_between(start, end)
    assert days == 10

def test_stock_mapper_to_stock_level_recalculation():
    """Verify that StockMapper uses the provided days to recalculate avg_sales."""
    row = pd.Series({
        'sales': 100.0,
        'balance': 50.0,
        'avg_sales': 0.0 # This should be ignored
    })
    
    # 1. Test with 100 days (100/100 = 1.0)
    stock_100 = StockMapper.to_stock_level(row, days=100)
    assert stock_100.avg_sales == 1.0
    
    # 2. Test with 50 days (100/50 = 2.0)
    stock_50 = StockMapper.to_stock_level(row, days=50)
    assert stock_50.avg_sales == 2.0

def test_get_sheet_duration_integration(tmp_path):
    """Test extracting duration from a mock CSV file header."""
    d = tmp_path / "data"
    d.mkdir()
    f = d / "test.csv"
    
    # Header format: some text with "DD/MM/YYYY HH:MM to DD/MM/YYYY HH:MM"
    header = "مبيعات الأصناف فى جميع المخازن الفترة من 01/01/2025 00:00 إلى 11/01/2025 00:00\n"
    content = "code,sales,balance\n123,10,20\n"
    
    f.write_text(header + content, encoding='utf-8-sig')
    
    days = get_sheet_duration_days(str(f))
    assert days == 10
