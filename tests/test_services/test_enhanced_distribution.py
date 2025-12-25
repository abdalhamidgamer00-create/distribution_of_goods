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

def test_stock_calculator_suppresses_need_at_threshold():
    """Verify that StockCalculator zeroes need if balance is >= 30."""
    # Coverage: 2.0 sales * 20 days = 40. balance = 25. Need = 15.
    stock_below = StockCalculator.calculate_stock_level(180, 25, 90)
    assert stock_below.needed > 0
    
    # Same as above but balance = 30. Need = 0.
    stock_at = StockCalculator.calculate_stock_level(180, 30, 90)
    assert stock_at.needed == 0
    
    # Balance = 50. Need = 0.
    stock_above = StockCalculator.calculate_stock_level(180, 50, 90)
    assert stock_above.needed == 0

def test_stock_calculator_suppresses_small_need():
    """Verify that StockCalculator suppresses need if coverage >= 15 and need < 10."""
    # Scenario: coverage = 20, balance = 12. Need = 8.
    # coverage >= 15 and need < 10 -> Should be suppressed to 0.
    stock = StockCalculator.calculate_stock_level(sales_quantity=90, balance_quantity=12, days_covered=90)
    # 90/90 = 1.0 avg. 1.0 * 20 = 20 coverage. 20 - 12 = 8 need.
    assert stock.needed == 0
    
    # Scenario: coverage = 20, balance = 5. Need = 15.
    # coverage >= 15 and need >= 10 -> Should NOT be suppressed.
    stock_needed = StockCalculator.calculate_stock_level(sales_quantity=90, balance_quantity=5, days_covered=90)
    assert stock_needed.needed == 15
    
    # Scenario: coverage = 8, balance = 4. Need = 4.
    # coverage < 15 -> Should NOT be suppressed.
    stock_low_coverage = StockCalculator.calculate_stock_level(sales_quantity=36, balance_quantity=4, days_covered=90)
    # 36/90 = 0.4 avg. 0.4 * 20 = 8 coverage. 8 - 4 = 4 need.
    assert stock_low_coverage.needed == 4

def test_stock_calculator_caps_need_at_max_balance():
    """Verify that StockCalculator caps need so total (balance + need) <= 30."""
    # Scenario: coverage = 100, balance = 25. 
    # Raw need = 75. 
    # Cap = 30 - 25 = 5.
    # Resulting need should be 5.
    stock = StockCalculator.calculate_stock_level(sales_quantity=450, balance_quantity=25, days_covered=90)
    # 450/90 = 5.0 avg. 5.0 * 20 = 100 coverage. 100 - 25 = 75 need.
    # After cap: min(75, 30-25) = 5.
    assert stock.needed == 5
    assert (stock.balance + stock.needed) == 30

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

def test_extract_dates_from_header_formats():
    """Verify that dates can be extracted from various Arabic header formats."""
    from src.domain.services.validation.dates import extract_dates_from_header
    
    # Format 1: Standard
    h1 = "الفترة من 01/01/2025 00:00 إلى 01/02/2025 00:00"
    s1, e1 = extract_dates_from_header(h1)
    assert s1.day == 1 and s1.month == 1
    assert e1.day == 1 and e1.month == 2
    
    # Format 2: No prefix
    h2 = "01/01/2025 10:00 05/01/2025 12:00"
    s2, e2 = extract_dates_from_header(h2)
    assert s2.hour == 10
    assert e2.day == 5
    
    # Format 3: Invalid
    h3 = "no dates here"
    s3, e3 = extract_dates_from_header(h3)
    assert s3 is None and e3 is None

def test_stock_mapper_consolidated_mapping():
    """Verify that StockMapper passes num_days to branch stocks."""
    row = pd.Series({
        'code': '123',
        'product_name': 'Test Product',
        'administration_sales': 100.0,
        'administration_balance': 50.0
    })
    
    # 10 days duration -> avg_sales should be 100/10 = 10.0
    consolidated = StockMapper.to_consolidated_stock(row, num_days=10)
    assert consolidated.branch_stocks['administration'].avg_sales == 10.0

def test_transfer_reader_parsing():
    """Verify that TransferReader correctly parses balances from CSV rows."""
    from src.infrastructure.repositories.io.transfer_reader import TransferReader
    
    reader = TransferReader("dummy")
    df = pd.DataFrame([{
        'code': '73396',
        'product_name': 'AVIL 6 AMP',
        'quantity_to_transfer': 1,
        'sender_balance': 1.0,
        'receiver_balance': 3.67
    }])
    
    transfers = reader._map_rows_to_transfers(df, "source", "target")
    assert len(transfers) == 1
    assert transfers[0].sender_balance == 1.0
    assert transfers[0].receiver_balance == 3.67
    assert transfers[0].from_branch.name == "source"

def test_stock_reader_fallback(tmp_path):
    """Verify that StockReader falls back to 90 days when header is missing."""
    from src.infrastructure.repositories.io.stock_reader import StockReader
    
    d = tmp_path / "analytics"
    d.mkdir()
    f = d / "no_header.csv"
    
    # Simple CSV without date header
    content = "code,sales,balance\n123,10,20\n"
    f.write_text(content, encoding='utf-8-sig')
    
    reader = StockReader(str(d))
    df, days = reader._read_csv_and_extract_days(str(f))
    
    # Should fallback to 90 days
    assert days == 90
    assert len(df) == 1
    assert str(df.iloc[0]['code']) == '123'
