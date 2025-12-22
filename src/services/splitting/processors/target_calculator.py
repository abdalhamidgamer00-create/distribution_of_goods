"""Calculate target transfer amount based on balance rules"""

import math


# Maximum allowed balance for a branch (no transfers if balance >= this value)
# This is the threshold above which a branch is considered "full" and won't receive transfers
MAXIMUM_BRANCH_BALANCE_THRESHOLD = 30


def _calculate_base_target(needed: float, balance: float) -> float:
    """Calculate base target amount based on needed and balance."""
    if balance >= MAXIMUM_BRANCH_BALANCE_THRESHOLD:
        return 0.0
    
    if needed + balance > MAXIMUM_BRANCH_BALANCE_THRESHOLD:
        return MAXIMUM_BRANCH_BALANCE_THRESHOLD - balance
    
    return needed


def _calculate_max_transfer(balance: float) -> float:
    """Calculate maximum transfer amount based on balance."""
    return MAXIMUM_BRANCH_BALANCE_THRESHOLD - balance


def _apply_proportional_limit(target_amount: float, proportional_allocation: float, balance: float) -> float:
    """Apply proportional allocation limits to target amount."""
    if proportional_allocation is None or proportional_allocation <= 0:
        return target_amount
    if balance >= MAXIMUM_BRANCH_BALANCE_THRESHOLD:
        return 0.0
    allocated_ceil = math.ceil(proportional_allocation)
    if allocated_ceil + balance > MAXIMUM_BRANCH_BALANCE_THRESHOLD:
        return min(target_amount, _calculate_max_transfer(balance))
    return min(target_amount, allocated_ceil)


def calculate_target_amount(needed: float, balance: float, proportional_allocation: float = None) -> float:
    """Calculate target transfer amount based on balance rules."""
    target_amount = _calculate_base_target(needed, balance)
    return _apply_proportional_limit(target_amount, proportional_allocation, balance)


def should_skip_transfer(balance: float) -> bool:
    """
    Check if transfer should be skipped based on balance.
    
    Args:
        balance: Current balance of the branch
        
    Returns:
        True if transfer should be skipped (balance >= 30), False otherwise
    """
    return balance >= MAXIMUM_BRANCH_BALANCE_THRESHOLD

