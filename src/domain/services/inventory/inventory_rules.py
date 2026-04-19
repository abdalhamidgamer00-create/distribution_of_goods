"""Pure domain rules for inventory adjustments and business logic."""

from src.shared.constants import (
    MAX_BALANCE_FOR_NEED_THRESHOLD,
    MIN_COVERAGE_FOR_SMALL_NEED_SUPPRESSION,
    MIN_NEED_THRESHOLD
)

def apply_scalar_rules(
    needed: int, 
    balance: float, 
    coverage: int
) -> int:
    """
    Applies stock adjustment rules to a single record (Pure Python).
    
    Args:
        needed: Initial calculated need
        balance: Current branch balance
        coverage: Target coverage quantity
        
    Returns:
        int: Adjusted needed quantity
    """
    adjusted_needed = needed

    # Rule 1: Individual Max Balance Suppression
    if balance >= MAX_BALANCE_FOR_NEED_THRESHOLD:
        return 0
        
    # Rule 2: Small Need Suppression
    # If coverage >= 15 and need < 10, suppress to 0
    if (coverage >= MIN_COVERAGE_FOR_SMALL_NEED_SUPPRESSION 
        and adjusted_needed < MIN_NEED_THRESHOLD):
        return 0
        
    # Rule 3: Max Balance Capping
    # Ensure that (balance + need) <= MAX_BALANCE_FOR_NEED_THRESHOLD
    if adjusted_needed > 0:
        available_space = max(0, MAX_BALANCE_FOR_NEED_THRESHOLD - balance)
        adjusted_needed = min(adjusted_needed, int(available_space))
        
    return adjusted_needed
