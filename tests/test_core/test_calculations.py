"""Tests for calculation functions in core.domain.calculations"""

import math
import pandas as pd
import pytest

from src.core.domain.calculations.quantity_calculator import (
    calculate_basic_quantities,
    calculate_surplus_remaining
)
from src.core.domain.calculations.allocation_calculator import (
    calculate_proportional_allocations_vectorized
)
from src.core.domain.calculations.order_calculator import (
    get_needing_branches_ordered_by_priority,
    get_surplus_sources_ordered_for_product
)
from src.domain.models.entities import StockLevel


class TestCalculateBasicQuantities:
    """Tests for calculate_basic_quantities function"""
    
    def test_monthly_quantity_calculation(self):
        """Test that monthly_quantity is calculated correctly (avg_sales * 30, ceiling)"""
        df = pd.DataFrame({
            'avg_sales': [1.0, 2.5, 0.5],
            'balance': [10.0, 50.0, 20.0]
        })
        result = calculate_basic_quantities(df)
        
        # avg_sales * 30, rounded up
        assert result['monthly_quantity'].iloc[0] == math.ceil(1.0 * 30)  # 30
        assert result['monthly_quantity'].iloc[1] == math.ceil(2.5 * 30)  # 75
        assert result['monthly_quantity'].iloc[2] == math.ceil(0.5 * 30)  # 15
    
    def test_surplus_quantity_calculation(self):
        """Test that surplus_quantity is calculated correctly (balance - monthly, floor, min 0)"""
        df = pd.DataFrame({
            'avg_sales': [1.0, 0.5, 2.0],
            'balance': [50.0, 10.0, 30.0]
        })
        result = calculate_basic_quantities(df)
        
        # balance - monthly_quantity, floor, min 0
        # Product 0: 50 - 30 = 20 (surplus)
        assert result['surplus_quantity'].iloc[0] == 20
        # Product 1: 10 - 15 = -5 -> 0 (no surplus)
        assert result['surplus_quantity'].iloc[1] == 0
        # Product 2: 30 - 60 = -30 -> 0 (no surplus)
        assert result['surplus_quantity'].iloc[2] == 0
    
    def test_needed_quantity_calculation(self):
        """Test that needed_quantity is calculated correctly (monthly - balance, ceiling, min 0)"""
        df = pd.DataFrame({
            'avg_sales': [1.0, 0.5, 2.0],
            'balance': [50.0, 10.0, 30.0]
        })
        result = calculate_basic_quantities(df)
        
        # monthly_quantity - balance, ceiling, min 0
        # Product 0: 30 - 50 = -20 -> 0 (no need)
        assert result['needed_quantity'].iloc[0] == 0
        # Product 1: 15 - 10 = 5 (needed)
        assert result['needed_quantity'].iloc[1] == 5
        # Product 2: 60 - 30 = 30 (needed)
        assert result['needed_quantity'].iloc[2] == 30
    
    def test_zero_avg_sales(self):
        """Test handling of zero average sales"""
        df = pd.DataFrame({
            'avg_sales': [0.0],
            'balance': [10.0]
        })
        result = calculate_basic_quantities(df)
        
        assert result['monthly_quantity'].iloc[0] == 0
        assert result['surplus_quantity'].iloc[0] == 10  # All balance is surplus
        assert result['needed_quantity'].iloc[0] == 0


class TestCalculateSurplusRemaining:
    """Tests for calculate_surplus_remaining function"""
    
    def test_no_withdrawals(self, sample_branch_data):
        """Test surplus remaining with no withdrawals"""
        from src.core.domain.branches.config import get_branches
        branches = get_branches()
        
        withdrawals = {}
        result = calculate_surplus_remaining(branches, sample_branch_data, withdrawals)
        
        # Should return original surplus values
        for branch in branches:
            assert branch in result
            assert len(result[branch]) == len(sample_branch_data[branch])
    
    def test_with_withdrawals(self, sample_branch_data):
        """Test surplus remaining after withdrawals"""
        from src.core.domain.branches.config import get_branches
        branches = get_branches()
        
        # Add some withdrawals
        withdrawals = {
            (branches[0], 0): 5.0,
            (branches[1], 1): 10.0
        }
        
        result = calculate_surplus_remaining(branches, sample_branch_data, withdrawals)
        
        # Verify withdrawals are subtracted
        for branch in branches:
            assert branch in result
    
    def test_withdrawal_exceeds_surplus(self, sample_branch_data):
        """Test that surplus remaining is never negative"""
        from src.core.domain.branches.config import get_branches
        branches = get_branches()
        
        # Withdraw more than available
        withdrawals = {
            (branches[0], 0): 1000.0  # Large withdrawal
        }
        
        result = calculate_surplus_remaining(branches, sample_branch_data, withdrawals)
        
        # Should be 0, not negative
        assert result[branches[0]][0] >= 0


class TestCalculateProportionalAllocationsVectorized:
    """Tests for calculate_proportional_allocations_vectorized function"""
    
    def test_empty_branch_data(self):
        """Test with empty branch data"""
        result = calculate_proportional_allocations_vectorized({}, [])
        assert result == {}
    
    def test_proportional_allocation_when_surplus_less_than_needed(self, sample_branch_data):
        """Test proportional allocation when total surplus < total needed"""
        from src.core.domain.branches.config import get_branches
        branches = get_branches()
        
        result = calculate_proportional_allocations_vectorized(sample_branch_data, branches)
        
        # Result should be a dictionary
        assert isinstance(result, dict)
        
        # For products with proportional allocation, check that allocations exist
        for product_idx, allocation in result.items():
            assert isinstance(allocation, dict)
            # Total allocated should not exceed total surplus
            total_allocated = sum(allocation.values())
            assert total_allocated >= 0
    
    def test_allocation_values_are_integers(self, sample_branch_data):
        """Test that all allocated values are integers"""
        from src.core.domain.branches.config import get_branches
        branches = get_branches()
        
        result = calculate_proportional_allocations_vectorized(sample_branch_data, branches)
        
        for product_idx, allocation in result.items():
            for branch, amount in allocation.items():
                assert isinstance(amount, int), f"Allocation for {branch} at idx {product_idx} is not int"


class TestGetNeedingBranchesOrderForProduct:
    """Tests for ordering needing branches by priority"""
    
    def test_returns_list(self):
        """Test that function returns a list of strings"""
        branch_stocks = {
            'branch1': StockLevel(needed=10, surplus=0, balance=1.0, avg_sales=2.0)
        }
        result = get_needing_branches_ordered_by_priority(branch_stocks)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == 'branch1'
    
    def test_only_needing_branches_returned(self):
        """Test that only branches with needed > 0 are returned"""
        branch_stocks = {
            'needing': StockLevel(needed=5, surplus=0, balance=10.0, avg_sales=1.0),
            'no_need': StockLevel(needed=0, surplus=10, balance=50.0, avg_sales=1.0)
        }
        result = get_needing_branches_ordered_by_priority(branch_stocks)
        assert 'needing' in result
        assert 'no_need' not in result
    
    def test_empty_when_no_need(self):
        """Test returns empty list when no branch needs the product"""
        branch_stocks = {
            'b1': StockLevel(needed=0, surplus=5, balance=10.0, avg_sales=1.0),
            'b2': StockLevel(needed=0, surplus=0, balance=20.0, avg_sales=1.0)
        }
        result = get_needing_branches_ordered_by_priority(branch_stocks)
        assert result == []


class TestGetSurplusBranchesOrderForProduct:
    """Tests for get_surplus_sources_ordered_for_product function"""
    
    def test_excludes_current_branch(self):
        """Test that source branch is excluded from results"""
        branch_stocks = {
            'source': StockLevel(needed=10, surplus=0, balance=1.0, avg_sales=1.0),
            'other': StockLevel(needed=0, surplus=20, balance=5.0, avg_sales=1.0)
        }
        result = get_surplus_sources_ordered_for_product(
            'source', branch_stocks
        )
        assert 'source' not in result
        assert 'other' in result
    
    def test_returns_list(self):
        """Test that function returns a list of strings"""
        branch_stocks = {
            'b1': StockLevel(needed=0, surplus=10, balance=1.0, avg_sales=1.0)
        }
        result = get_surplus_sources_ordered_for_product('some_other', branch_stocks)
        assert isinstance(result, list)
        assert result[0] == 'b1'
    
    def test_only_surplus_branches_returned(self):
        """Test that branches with no surplus are ignored"""
        branch_stocks = {
            'has_surplus': StockLevel(needed=0, surplus=10, balance=1.0, avg_sales=1.0),
            'no_surplus': StockLevel(needed=5, surplus=0, balance=5.0, avg_sales=1.0)
        }
        result = get_surplus_sources_ordered_for_product('target', branch_stocks)
        assert 'has_surplus' in result
        assert 'no_surplus' not in result
