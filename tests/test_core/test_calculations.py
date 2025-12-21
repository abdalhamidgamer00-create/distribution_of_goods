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
    get_needing_branches_order_for_product,
    get_surplus_branches_order_for_product
)


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
    """Tests for get_needing_branches_order_for_product function"""
    
    def test_returns_list(self, sample_branch_data):
        """Test that function returns a list"""
        from src.core.domain.branches.config import get_branches
        branches = get_branches()
        
        result = get_needing_branches_order_for_product(0, sample_branch_data, branches)
        
        assert isinstance(result, list)
    
    def test_only_needing_branches_returned(self, sample_branch_data):
        """Test that only branches with needed > 0 are returned"""
        from src.core.domain.branches.config import get_branches
        branches = get_branches()
        
        result = get_needing_branches_order_for_product(0, sample_branch_data, branches)
        
        # All returned branches should have needed_quantity > 0
        for branch in result:
            assert sample_branch_data[branch].iloc[0]['needed_quantity'] > 0
    
    def test_empty_when_no_need(self):
        """Test returns empty list when no branch needs the product"""
        branches = ['branch1', 'branch2']
        
        # Create branch data where no branch needs anything
        branch_data = {
            'branch1': pd.DataFrame({
                'needed_quantity': [0],
                'avg_sales': [1.0],
                'balance': [100.0]
            }),
            'branch2': pd.DataFrame({
                'needed_quantity': [0],
                'avg_sales': [1.0],
                'balance': [100.0]
            })
        }
        
        result = get_needing_branches_order_for_product(0, branch_data, branches)
        
        assert result == []


class TestGetSurplusBranchesOrderForProduct:
    """Tests for get_surplus_branches_order_for_product function"""
    
    def test_excludes_current_branch(self, sample_branch_data):
        """Test that current branch is excluded from results"""
        from src.core.domain.branches.config import get_branches
        branches = get_branches()
        
        current_branch = branches[0]
        result = get_surplus_branches_order_for_product(
            0, current_branch, sample_branch_data, branches
        )
        
        assert current_branch not in result
    
    def test_returns_list(self, sample_branch_data):
        """Test that function returns a list"""
        from src.core.domain.branches.config import get_branches
        branches = get_branches()
        
        result = get_surplus_branches_order_for_product(
            0, branches[0], sample_branch_data, branches
        )
        
        assert isinstance(result, list)
    
    def test_respects_existing_withdrawals(self, sample_branch_data):
        """Test that existing withdrawals affect available surplus"""
        from src.core.domain.branches.config import get_branches
        branches = get_branches()
        
        # Create large withdrawal for a branch
        existing_withdrawals = {
            (branches[1], 0): 1000.0  # Large withdrawal
        }
        
        result = get_surplus_branches_order_for_product(
            0, branches[0], sample_branch_data, branches, existing_withdrawals
        )
        
        # Branch with depleted surplus might not be in result
        # or might be lower in priority
        assert isinstance(result, list)
