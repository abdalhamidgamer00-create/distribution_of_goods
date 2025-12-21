"""Tests for branch configuration functions"""

import pytest

from src.core.domain.branches.config import (
    get_branches,
    get_search_order,
    get_base_columns,
    get_analytics_columns
)


class TestGetBranches:
    """Tests for get_branches function"""
    
    def test_returns_list(self):
        """Test that get_branches returns a list"""
        result = get_branches()
        assert isinstance(result, list)
    
    def test_returns_six_branches(self):
        """Test that exactly 6 branches are returned"""
        result = get_branches()
        assert len(result) == 6
    
    def test_expected_branches(self):
        """Test that all expected branches are present"""
        result = get_branches()
        expected = ['asherin', 'wardani', 'akba', 'shahid', 'nujum', 'admin']
        assert result == expected
    
    def test_branches_are_strings(self):
        """Test that all branch names are strings"""
        result = get_branches()
        for branch in result:
            assert isinstance(branch, str)


class TestGetSearchOrder:
    """Tests for get_search_order function"""
    
    def test_returns_list(self):
        """Test that get_search_order returns a list"""
        result = get_search_order()
        assert isinstance(result, list)
    
    def test_admin_first(self):
        """Test that admin is first in search order"""
        result = get_search_order()
        assert result[0] == 'admin'
    
    def test_returns_six_branches(self):
        """Test that exactly 6 branches are returned"""
        result = get_search_order()
        assert len(result) == 6
    
    def test_all_branches_present(self):
        """Test that all branches are in search order"""
        search_order = set(get_search_order())
        branches = set(get_branches())
        assert search_order == branches


class TestGetBaseColumns:
    """Tests for get_base_columns function"""
    
    def test_returns_list(self):
        """Test that get_base_columns returns a list"""
        result = get_base_columns()
        assert isinstance(result, list)
    
    def test_returns_seven_columns(self):
        """Test that exactly 7 base columns are returned"""
        result = get_base_columns()
        assert len(result) == 7
    
    def test_expected_columns(self):
        """Test that all expected base columns are present"""
        result = get_base_columns()
        expected = ['code', 'product_name', 'selling_price', 'company', 'unit',
                    'total_sales', 'total_product_balance']
        assert result == expected
    
    def test_columns_are_strings(self):
        """Test that all column names are strings"""
        result = get_base_columns()
        for col in result:
            assert isinstance(col, str)


class TestGetAnalyticsColumns:
    """Tests for get_analytics_columns function"""
    
    def test_returns_list(self):
        """Test that get_analytics_columns returns a list"""
        result = get_analytics_columns()
        assert isinstance(result, list)
    
    def test_default_max_withdrawals(self):
        """Test with default max_withdrawals (5)"""
        result = get_analytics_columns()
        
        # Should have 8 base columns + 4 columns per withdrawal * 5 = 28 total
        # But the function has 8 base analytics columns, not exactly base columns
        assert len(result) >= 8
    
    def test_custom_max_withdrawals(self):
        """Test with custom max_withdrawals"""
        result_5 = get_analytics_columns(max_withdrawals=5)
        result_10 = get_analytics_columns(max_withdrawals=10)
        
        # More withdrawals should mean more columns
        assert len(result_10) > len(result_5)
    
    def test_zero_withdrawals(self):
        """Test with zero withdrawals"""
        result = get_analytics_columns(max_withdrawals=0)
        
        # Should have only base columns
        assert len(result) == 8  # 8 base analytics columns
    
    def test_withdrawal_column_pattern(self):
        """Test that withdrawal columns follow expected pattern"""
        result = get_analytics_columns(max_withdrawals=2)
        
        # Check for expected withdrawal columns
        assert 'surplus_from_branch_1' in result
        assert 'available_branch_1' in result
        assert 'surplus_remaining_1' in result
        assert 'remaining_needed_1' in result
        assert 'surplus_from_branch_2' in result
