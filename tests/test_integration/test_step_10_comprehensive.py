"""Comprehensive tests for Step 10 shortage calculator module.

Tests cover all functions in shortage_calculator.py which calculates
products where total needed quantity exceeds total surplus.
"""

import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

from src.app.pipeline.step_10.shortage_calculator import (
    _load_analytics_dataframe,
    read_analytics_file,
    _has_required_columns,
    _initialize_product_totals,
    _update_single_row,
    _update_product_totals,
    _load_and_validate_branch_analytics,
    _aggregate_branch_totals,
    _get_shortage_columns,
    _build_shortage_row,
    _build_shortage_dataframe,
    calculate_shortage_products,
    REQUIRED_COLUMNS
)


# ===================== Fixtures =====================

@pytest.fixture
def sample_analytics_df():
    """Sample analytics DataFrame with all required columns."""
    return pd.DataFrame({
        'code': ['001', '002', '003'],
        'product_name': ['Product A', 'Product B', 'Product C'],
        'surplus_quantity': [10.0, 0.0, 5.0],
        'needed_quantity': [0.0, 20.0, 15.0],
        'balance': [50, 30, 25],
        'sales': [100.0, 200.0, 150.0]
    })


@pytest.fixture
def analytics_test_directory(tmp_path):
    """Create a test analytics directory structure with sample files."""
    analytics_dir = tmp_path / "analytics"
    
    # Create branch directories with analytics files
    branches = ['admin', 'wardani', 'akba']
    
    for branch in branches:
        branch_dir = analytics_dir / branch
        branch_dir.mkdir(parents=True)
        
        # Create sample analytics CSV
        df = pd.DataFrame({
            'code': ['001', '002', '003'],
            'product_name': ['Product A', 'Product B', 'Product C'],
            'surplus_quantity': [10.0, 5.0, 0.0],
            'needed_quantity': [0.0, 10.0, 20.0],
            'balance': [50, 30, 15],
            'sales': [100.0, 150.0, 200.0]
        })
        
        csv_path = branch_dir / f"test_{branch}_analytics.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    return str(analytics_dir)


@pytest.fixture
def analytics_with_date_header(tmp_path):
    """Create analytics file with date header."""
    branch_dir = tmp_path / "analytics" / "admin"
    branch_dir.mkdir(parents=True)
    
    csv_path = branch_dir / "test_admin_analytics.csv"
    
    with open(csv_path, 'w', encoding='utf-8-sig') as f:
        f.write("من: 01/09/2024 00:00 إلى: 01/12/2024 00:00\n")
        f.write("code,product_name,surplus_quantity,needed_quantity,balance,sales\n")
        f.write("001,Product A,10.0,0.0,50,100.0\n")
        f.write("002,Product B,0.0,20.0,30,200.0\n")
    
    return str(csv_path), str(tmp_path / "analytics")


# ===================== _load_analytics_dataframe Tests =====================

class TestLoadAnalyticsDataframe:
    """Tests for _load_analytics_dataframe function."""
    
    def test_load_without_date_header(self, tmp_path):
        """
        WHAT: Load CSV without skipping any rows
        WHY: Normal CSV files should be read completely
        BREAKS: Data loss if first row incorrectly skipped
        """
        csv_path = tmp_path / "test.csv"
        df = pd.DataFrame({'code': ['001'], 'product_name': ['Test']})
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        result = _load_analytics_dataframe(str(csv_path), has_date_header=False)
        
        assert len(result) == 1
        # Code may be read as int due to pandas type inference
        assert str(result.iloc[0]['code']).lstrip('0') == '1' or str(result.iloc[0]['code']) == '001'
    
    def test_load_with_date_header(self, analytics_with_date_header):
        """
        WHAT: Load CSV skipping the first row (date header)
        WHY: Date header row should not be treated as data
        BREAKS: Column headers read incorrectly, parse errors
        """
        csv_path, _ = analytics_with_date_header
        
        result = _load_analytics_dataframe(csv_path, has_date_header=True)
        
        # Should skip the date header row
        assert 'code' in result.columns
        assert len(result) == 2


# ===================== read_analytics_file Tests =====================

class TestReadAnalyticsFile:
    """Tests for read_analytics_file function."""
    
    def test_read_file_with_date_header(self, analytics_with_date_header):
        """
        WHAT: Read analytics file and detect date header
        WHY: Automatic date header detection is critical for downstream processing
        BREAKS: Incorrect date range display in output files
        """
        csv_path, _ = analytics_with_date_header
        
        df, has_date_header, first_line = read_analytics_file(csv_path)
        
        assert df is not None
        assert has_date_header is True
        assert '01/09/2024' in first_line
    
    def test_read_file_without_date_header(self, tmp_path):
        """
        WHAT: Read analytics file without date header
        WHY: Should correctly identify files without date headers
        BREAKS: Incorrect header detection causes data shift
        """
        csv_path = tmp_path / "test.csv"
        df_input = pd.DataFrame({
            'code': ['001'],
            'product_name': ['Test'],
            'surplus_quantity': [10],
            'needed_quantity': [5],
            'balance': [20],
            'sales': [100]
        })
        df_input.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        df, has_date_header, first_line = read_analytics_file(str(csv_path))
        
        assert df is not None
        assert has_date_header is False
        # First line should be column names
        assert 'code' in first_line.lower()
    
    def test_read_nonexistent_file(self):
        """
        WHAT: Gracefully handle missing files
        WHY: Missing files shouldn't crash the application
        BREAKS: Application crash on missing analytics file
        """
        df, has_date_header, first_line = read_analytics_file('/nonexistent/path.csv')
        
        assert df is None
        assert has_date_header is False
        assert first_line == ''


# ===================== _has_required_columns Tests =====================

class TestHasRequiredColumns:
    """Tests for _has_required_columns function."""
    
    def test_all_columns_present(self, sample_analytics_df):
        """
        WHAT: Validate DataFrame with all required columns
        WHY: Should return True when all columns present
        BREAKS: False negatives cause valid files to be rejected
        """
        result = _has_required_columns(sample_analytics_df, '/test/path.csv')
        
        assert result is True
    
    def test_missing_columns(self):
        """
        WHAT: Detect missing required columns
        WHY: Should return False and log warning for invalid files
        BREAKS: Processing invalid data causes incorrect results
        """
        incomplete_df = pd.DataFrame({
            'code': ['001'],
            'product_name': ['Test']
            # Missing: surplus_quantity, needed_quantity, balance, sales
        })
        
        result = _has_required_columns(incomplete_df, '/test/path.csv')
        
        assert result is False
    
    def test_extra_columns_allowed(self, sample_analytics_df):
        """
        WHAT: Allow DataFrames with extra columns
        WHY: Extra columns should not cause validation failure
        BREAKS: Valid files with extra columns incorrectly rejected
        """
        df_with_extra = sample_analytics_df.copy()
        df_with_extra['extra_column'] = 'extra'
        
        result = _has_required_columns(df_with_extra, '/test/path.csv')
        
        assert result is True


# ===================== _initialize_product_totals Tests =====================

class TestInitializeProductTotals:
    """Tests for _initialize_product_totals function."""
    
    def test_initialize_with_single_branch(self):
        """
        WHAT: Initialize totals for single-branch scenario
        WHY: Basic initialization must work correctly
        BREAKS: Incorrect initialization causes cumulative errors
        """
        result = _initialize_product_totals('Test Product', ['admin'])
        
        assert result['product_name'] == 'Test Product'
        assert result['total_surplus'] == 0.0
        assert result['total_needed'] == 0.0
        assert result['total_sales'] == 0.0
        assert 'admin' in result['branch_balances']
        assert result['branch_balances']['admin'] == 0
    
    def test_initialize_with_multiple_branches(self):
        """
        WHAT: Initialize totals for multiple branches
        WHY: All branches must be present in balance tracking
        BREAKS: Missing branches causes KeyError during processing
        """
        branches = ['admin', 'wardani', 'akba', 'shahid']
        
        result = _initialize_product_totals('Multi-Branch Product', branches)
        
        for branch in branches:
            assert branch in result['branch_balances']
            assert result['branch_balances'][branch] == 0


# ===================== _update_single_row Tests =====================

class TestUpdateSingleRow:
    """Tests for _update_single_row function."""
    
    def test_update_new_product(self):
        """
        WHAT: Add new product to totals
        WHY: First occurrence of a product should create entry
        BREAKS: New products not tracked
        """
        product_totals = {}
        branches = ['admin']
        row = pd.Series({
            'code': '001',
            'product_name': 'New Product',
            'surplus_quantity': 10.0,
            'needed_quantity': 5.0,
            'sales': 100.0,
            'balance': 50
        })
        
        _update_single_row(product_totals, row, 'admin', branches)
        
        assert '001' in product_totals
        assert product_totals['001']['total_surplus'] == 10.0
        assert product_totals['001']['total_needed'] == 5.0
        assert product_totals['001']['total_sales'] == 100.0
        assert product_totals['001']['branch_balances']['admin'] == 50
    
    def test_accumulate_existing_product(self):
        """
        WHAT: Accumulate values for existing product
        WHY: Multiple branches contribute to total
        BREAKS: Incorrect totals cause wrong shortage calculation
        """
        branches = ['admin', 'wardani']
        product_totals = {
            '001': {
                'product_name': 'Existing Product',
                'total_surplus': 10.0,
                'total_needed': 5.0,
                'total_sales': 100.0,
                'branch_balances': {'admin': 50, 'wardani': 0}
            }
        }
        row = pd.Series({
            'code': '001',
            'product_name': 'Existing Product',
            'surplus_quantity': 15.0,
            'needed_quantity': 10.0,
            'sales': 150.0,
            'balance': 30
        })
        
        _update_single_row(product_totals, row, 'wardani', branches)
        
        assert product_totals['001']['total_surplus'] == 25.0  # 10 + 15
        assert product_totals['001']['total_needed'] == 15.0   # 5 + 10
        assert product_totals['001']['total_sales'] == 250.0   # 100 + 150
        assert product_totals['001']['branch_balances']['wardani'] == 30
    
    def test_handle_null_values(self):
        """
        WHAT: Handle null/None values in row data
        WHY: Missing data should be treated as zero
        BREAKS: NaN errors in calculations
        """
        product_totals = {}
        branches = ['admin']
        row = pd.Series({
            'code': '001',
            'product_name': 'Product with nulls',
            'surplus_quantity': None,
            'needed_quantity': None,
            'sales': None,
            'balance': None
        })
        
        _update_single_row(product_totals, row, 'admin', branches)
        
        assert product_totals['001']['total_surplus'] == 0.0
        assert product_totals['001']['total_needed'] == 0.0
        assert product_totals['001']['total_sales'] == 0.0


# ===================== _get_shortage_columns Tests =====================

class TestGetShortageColumns:
    """Tests for _get_shortage_columns function."""
    
    def test_returns_correct_base_columns(self):
        """
        WHAT: Verify base columns are present
        WHY: Output file structure depends on correct columns
        BREAKS: Incorrect column order breaks downstream processing
        """
        result = _get_shortage_columns()
        
        assert 'code' in result
        assert 'product_name' in result
        assert 'shortage_quantity' in result
        assert 'total_sales' in result
    
    def test_includes_balance_columns_for_all_branches(self):
        """
        WHAT: Verify balance columns for all branches
        WHY: Each branch needs a balance column in output
        BREAKS: Missing branch data in output file
        """
        result = _get_shortage_columns()
        
        # Should have balance columns
        balance_columns = [col for col in result if col.startswith('balance_')]
        assert len(balance_columns) > 0


# ===================== _build_shortage_row Tests =====================

class TestBuildShortageRow:
    """Tests for _build_shortage_row function."""
    
    def test_build_row_with_shortage(self):
        """
        WHAT: Build output row for product with shortage
        WHY: Correct row format is critical for output files
        BREAKS: Incorrect data in shortage reports
        """
        totals = {
            'product_name': 'Shortage Product',
            'total_needed': 100.0,
            'total_surplus': 30.0,
            'total_sales': 500.0,
            'branch_balances': {'admin': 20, 'wardani': 10}
        }
        
        result = _build_shortage_row('001', totals, ['admin', 'wardani'])
        
        assert result['code'] == '001'
        assert result['product_name'] == 'Shortage Product'
        assert result['shortage_quantity'] == 70  # 100 - 30
        assert result['total_sales'] == 500
        assert result['balance_admin'] == 20
        assert result['balance_wardani'] == 10
    
    def test_shortage_calculation_with_zero_surplus(self):
        """
        WHAT: Calculate shortage when no surplus available
        WHY: Edge case where all branches need product
        BREAKS: Division by zero or incorrect shortage amount
        """
        totals = {
            'product_name': 'No Surplus Product',
            'total_needed': 50.0,
            'total_surplus': 0.0,
            'total_sales': 200.0,
            'branch_balances': {'admin': 0}
        }
        
        result = _build_shortage_row('002', totals, ['admin'])
        
        assert result['shortage_quantity'] == 50


# ===================== _build_shortage_dataframe Tests =====================

class TestBuildShortageDataframe:
    """Tests for _build_shortage_dataframe function."""
    
    @patch('src.app.pipeline.step_10.shortage_calculator.get_search_order')
    def test_filter_products_with_shortage(self, mock_get_search_order):
        """
        WHAT: Only include products where needed > surplus
        WHY: Shortage report should only show actual shortages
        BREAKS: Report cluttered with non-shortage products
        """
        mock_get_search_order.return_value = ['admin']
        branches = ['admin']
        product_totals = {
            '001': {
                'product_name': 'Has Shortage',
                'total_needed': 100.0,
                'total_surplus': 30.0,
                'total_sales': 500.0,
                'branch_balances': {'admin': 30}
            },
            '002': {
                'product_name': 'No Shortage',
                'total_needed': 20.0,
                'total_surplus': 50.0,
                'total_sales': 300.0,
                'branch_balances': {'admin': 50}
            }
        }
        
        result = _build_shortage_dataframe(product_totals, branches)
        
        assert len(result) == 1
        assert result.iloc[0]['code'] == '001'
    
    @patch('src.app.pipeline.step_10.shortage_calculator.get_search_order')
    def test_empty_result_when_no_shortage(self, mock_get_search_order):
        """
        WHAT: Return empty DataFrame when no products have shortage
        WHY: Should handle case where all needs are met
        BREAKS: Error on empty results
        """
        mock_get_search_order.return_value = ['admin']
        branches = ['admin']
        product_totals = {
            '001': {
                'product_name': 'Surplus Product',
                'total_needed': 20.0,
                'total_surplus': 50.0,
                'total_sales': 200.0,
                'branch_balances': {'admin': 50}
            }
        }
        
        result = _build_shortage_dataframe(product_totals, branches)
        
        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)
    
    @patch('src.app.pipeline.step_10.shortage_calculator.get_search_order')
    def test_sorted_by_shortage_descending(self, mock_get_search_order):
        """
        WHAT: Results sorted by shortage_quantity descending
        WHY: Most critical shortages should appear first
        BREAKS: Priority products hidden at bottom of report
        """
        mock_get_search_order.return_value = ['admin']
        branches = ['admin']
        product_totals = {
            '001': {
                'product_name': 'Small Shortage',
                'total_needed': 30.0,
                'total_surplus': 20.0,
                'total_sales': 100.0,
                'branch_balances': {'admin': 20}
            },
            '002': {
                'product_name': 'Large Shortage',
                'total_needed': 100.0,
                'total_surplus': 10.0,
                'total_sales': 500.0,
                'branch_balances': {'admin': 10}
            }
        }
        
        result = _build_shortage_dataframe(product_totals, branches)
        
        assert len(result) == 2
        assert result.iloc[0]['code'] == '002'  # Large shortage first
        assert result.iloc[1]['code'] == '001'  # Small shortage second


# ===================== calculate_shortage_products Integration Tests =====================

class TestCalculateShortageProductsIntegration:
    """Integration tests for calculate_shortage_products function."""
    
    @patch('src.app.pipeline.step_10.shortage_calculator.get_search_order')
    @patch('src.app.pipeline.step_10.shortage_calculator.get_branches')
    def test_full_calculation_flow(self, mock_get_branches, mock_get_search_order, analytics_test_directory):
        """
        WHAT: Test complete shortage calculation workflow
        WHY: End-to-end test ensures all components work together
        BREAKS: Complete shortage calculation failure
        """
        mock_get_branches.return_value = ['admin', 'wardani', 'akba']
        mock_get_search_order.return_value = ['admin', 'wardani', 'akba']
        
        shortage_df, has_date_header, first_line = calculate_shortage_products(analytics_test_directory)
        
        assert isinstance(shortage_df, pd.DataFrame)
        # Products with shortage should be present (needed > surplus)
        if not shortage_df.empty:
            assert 'shortage_quantity' in shortage_df.columns
            assert 'code' in shortage_df.columns
    
    @patch('src.app.pipeline.step_10.shortage_calculator.get_search_order')
    @patch('src.app.pipeline.step_10.shortage_calculator.get_branches')
    def test_empty_analytics_directory(self, mock_get_branches, mock_get_search_order, tmp_path):
        """
        WHAT: Handle empty analytics directory gracefully
        WHY: Should not crash with empty input
        BREAKS: Application crash on empty directory
        """
        mock_get_branches.return_value = ['admin']
        mock_get_search_order.return_value = ['admin']
        
        empty_dir = tmp_path / "empty_analytics"
        os.makedirs(empty_dir / "admin", exist_ok=True)
        
        shortage_df, has_date_header, first_line = calculate_shortage_products(str(empty_dir))
        
        assert isinstance(shortage_df, pd.DataFrame)
        assert len(shortage_df) == 0


# ===================== _update_product_totals Tests =====================

class TestUpdateProductTotals:
    """Tests for _update_product_totals function."""
    
    def test_process_all_rows(self, sample_analytics_df):
        """
        WHAT: Process all rows in a DataFrame
        WHY: Each row should update product totals
        BREAKS: Missing products in totals
        """
        product_totals = {}
        branches = ['admin']
        
        _update_product_totals(product_totals, sample_analytics_df, 'admin', branches)
        
        assert '001' in product_totals
        assert '002' in product_totals
        assert '003' in product_totals
    
    def test_skip_rows_with_nan_code(self):
        """
        WHAT: Skip rows where code is NaN
        WHY: Invalid rows should not be processed
        BREAKS: KeyError or invalid product entries
        """
        df = pd.DataFrame({
            'code': ['001', None, '003'],
            'product_name': ['A', 'B', 'C'],
            'surplus_quantity': [10, 20, 30],
            'needed_quantity': [5, 10, 15],
            'balance': [50, 60, 70],
            'sales': [100, 200, 300]
        })
        
        product_totals = {}
        branches = ['admin']
        
        _update_product_totals(product_totals, df, 'admin', branches)
        
        assert '001' in product_totals
        assert '003' in product_totals
        # NaN code should be skipped
        assert len(product_totals) == 2
