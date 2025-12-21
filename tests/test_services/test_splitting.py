"""Tests for splitting service functions"""

import math
import pandas as pd
import pytest

from src.services.splitting.processors.target_calculator import (
    calculate_target_amount,
    should_skip_transfer,
    MAX_ALLOWED_BALANCE
)
from src.services.splitting.processors.surplus_helpers import (
    calculate_available_surplus,
    process_single_withdrawal
)


class TestCalculateTargetAmount:
    """Tests for calculate_target_amount function"""
    
    def test_balance_above_max_returns_zero(self):
        """Test that balance >= 30 returns 0"""
        result = calculate_target_amount(needed=10.0, balance=35.0)
        assert result == 0.0
        
        result = calculate_target_amount(needed=10.0, balance=30.0)
        assert result == 0.0
    
    def test_needed_plus_balance_exceeds_max(self):
        """Test when needed + balance > 30"""
        # balance = 20, needed = 15, needed + balance = 35 > 30
        # Should return 30 - 20 = 10
        result = calculate_target_amount(needed=15.0, balance=20.0)
        assert result == MAX_ALLOWED_BALANCE - 20.0  # 10
    
    def test_needed_plus_balance_below_max(self):
        """Test when needed + balance <= 30"""
        # balance = 10, needed = 5, needed + balance = 15 <= 30
        # Should return full needed amount
        result = calculate_target_amount(needed=5.0, balance=10.0)
        assert result == 5.0
    
    def test_zero_balance(self):
        """Test with zero balance"""
        result = calculate_target_amount(needed=10.0, balance=0.0)
        assert result == 10.0
    
    def test_with_proportional_allocation(self):
        """Test with proportional allocation provided"""
        result = calculate_target_amount(
            needed=20.0, 
            balance=5.0, 
            proportional_allocation=10.0
        )
        
        # Should respect proportional allocation
        assert result <= 10.0 or result <= MAX_ALLOWED_BALANCE - 5.0
    
    def test_proportional_allocation_exceeds_max(self):
        """Test when proportional + balance > max"""
        result = calculate_target_amount(
            needed=50.0,
            balance=25.0,
            proportional_allocation=20.0
        )
        
        # Should cap at 30 - 25 = 5
        assert result <= MAX_ALLOWED_BALANCE - 25.0


class TestShouldSkipTransfer:
    """Tests for should_skip_transfer function"""
    
    def test_balance_above_max(self):
        """Test that balance >= 30 returns True"""
        assert should_skip_transfer(35.0) is True
        assert should_skip_transfer(30.0) is True
    
    def test_balance_below_max(self):
        """Test that balance < 30 returns False"""
        assert should_skip_transfer(29.0) is False
        assert should_skip_transfer(0.0) is False
        assert should_skip_transfer(15.0) is False
    
    def test_boundary_value(self):
        """Test exact boundary value"""
        assert should_skip_transfer(30.0) is True
        assert should_skip_transfer(29.99) is False


class TestCalculateAvailableSurplus:
    """Tests for calculate_available_surplus function"""
    
    def test_no_withdrawals(self):
        """Test surplus calculation with no prior withdrawals"""
        branch_data = {
            'branch1': pd.DataFrame({
                'surplus_quantity': [100.0, 50.0, 25.0]
            })
        }
        
        result = calculate_available_surplus(
            branch_data, 'branch1', 0, {}
        )
        
        assert result == 100
    
    def test_with_withdrawals(self):
        """Test surplus after withdrawals"""
        branch_data = {
            'branch1': pd.DataFrame({
                'surplus_quantity': [100.0, 50.0, 25.0]
            })
        }
        
        existing_withdrawals = {('branch1', 0): 30.0}
        
        result = calculate_available_surplus(
            branch_data, 'branch1', 0, existing_withdrawals
        )
        
        assert result == math.floor(100.0 - 30.0)  # 70
    
    def test_withdrawals_exceed_surplus(self):
        """Test that result is never negative"""
        branch_data = {
            'branch1': pd.DataFrame({
                'surplus_quantity': [50.0]
            })
        }
        
        existing_withdrawals = {('branch1', 0): 60.0}
        
        result = calculate_available_surplus(
            branch_data, 'branch1', 0, existing_withdrawals
        )
        
        assert result >= 0


class TestProcessSingleWithdrawal:
    """Tests for process_single_withdrawal function"""
    
    def test_basic_withdrawal(self):
        """Test basic withdrawal processing"""
        withdrawals = {}
        withdrawals_for_row = []
        
        remaining, target = process_single_withdrawal(
            other_branch='branch1',
            idx=0,
            remaining_needed=10.0,
            target_amount=10.0,
            available_surplus=5.0,
            withdrawals=withdrawals,
            withdrawals_for_row=withdrawals_for_row
        )
        
        # Should withdraw 5 (the available surplus)
        assert len(withdrawals_for_row) == 1
        assert withdrawals_for_row[0]['surplus_from_branch'] == 5
        assert withdrawals_for_row[0]['available_branch'] == 'branch1'
        assert ('branch1', 0) in withdrawals
    
    def test_withdrawal_updates_remaining(self):
        """Test that remaining values are updated correctly"""
        withdrawals = {}
        withdrawals_for_row = []
        
        remaining, target = process_single_withdrawal(
            other_branch='branch1',
            idx=0,
            remaining_needed=10.0,
            target_amount=10.0,
            available_surplus=3.0,
            withdrawals=withdrawals,
            withdrawals_for_row=withdrawals_for_row
        )
        
        # remaining_needed should decrease by 3
        assert remaining == math.ceil(10.0 - 3.0)  # 7
        assert target == math.ceil(10.0 - 3.0)  # 7
    
    def test_multiple_withdrawals_accumulate(self):
        """Test that multiple withdrawals from same branch accumulate"""
        withdrawals = {('branch1', 0): 5.0}  # Prior withdrawal
        withdrawals_for_row = []
        
        remaining, target = process_single_withdrawal(
            other_branch='branch1',
            idx=0,
            remaining_needed=10.0,
            target_amount=10.0,
            available_surplus=3.0,
            withdrawals=withdrawals,
            withdrawals_for_row=withdrawals_for_row
        )
        
        # Should add to existing
        assert withdrawals[('branch1', 0)] == 5.0 + 3.0  # 8.0
    
    def test_zero_available_surplus(self):
        """Test with zero available surplus"""
        withdrawals = {}
        withdrawals_for_row = []
        
        remaining, target = process_single_withdrawal(
            other_branch='branch1',
            idx=0,
            remaining_needed=10.0,
            target_amount=10.0,
            available_surplus=0.0,
            withdrawals=withdrawals,
            withdrawals_for_row=withdrawals_for_row
        )
        
        # No withdrawal should be made
        assert len(withdrawals_for_row) == 0
        assert remaining == 10.0
        assert target == 10.0
