"""Calculate target transfer amount based on balance rules"""

import math


# Maximum allowed balance for a branch (no transfers if balance >= this value)
MAX_ALLOWED_BALANCE = 15


def calculate_target_amount(
    needed: float,
    balance: float,
    proportional_allocation: float = None
) -> float:
    """
    Calculate target transfer amount based on balance rules.
    
    Rules:
    1. If balance >= 15: No transfer (return 0)
    2. If balance < 15 and needed + balance > 15: Transfer only (15 - balance)
    3. If balance < 15 and needed + balance <= 15: Transfer full needed amount
    4. If proportional_allocation is provided, apply same rules to it
    
    Args:
        needed: Needed quantity for the branch
        balance: Current balance of the branch
        proportional_allocation: Optional proportional allocation amount
        
    Returns:
        Target amount to transfer (as integer)
    """
    # Rule 1: No transfer if balance >= 15
    if balance >= MAX_ALLOWED_BALANCE:
        return 0.0
    
    # Rule 2 & 3: Calculate based on needed + balance
    if balance < MAX_ALLOWED_BALANCE:
        if needed + balance > MAX_ALLOWED_BALANCE:
            # Rule 2: Transfer only what completes to 15
            target_amount = MAX_ALLOWED_BALANCE - balance
        else:
            # Rule 3: Transfer full needed amount
            target_amount = needed
    else:
        # Should not reach here (balance >= 15 already checked)
        target_amount = 0.0
    
    # Apply proportional allocation if provided
    if proportional_allocation is not None and proportional_allocation > 0:
        allocated_ceil = math.ceil(proportional_allocation)
        if balance < MAX_ALLOWED_BALANCE:
            if allocated_ceil + balance > MAX_ALLOWED_BALANCE:
                # Cannot transfer more than (15 - balance)
                target_amount = min(target_amount, MAX_ALLOWED_BALANCE - balance)
            else:
                # Can transfer full allocated amount
                target_amount = min(target_amount, allocated_ceil)
        else:
            target_amount = 0.0
    
    return target_amount


def should_skip_transfer(balance: float) -> bool:
    """
    Check if transfer should be skipped based on balance.
    
    Args:
        balance: Current balance of the branch
        
    Returns:
        True if transfer should be skipped (balance >= 15), False otherwise
    """
    return balance >= MAX_ALLOWED_BALANCE

