"""Helper functions for surplus calculations"""

import math


def calculate_available_surplus(
    branch_data: dict, 
    branch: str, 
    idx: int, 
    existing_withdrawals: dict
) -> float:
    """
    Calculate available surplus for a product after accounting for withdrawals.
    Uses floor rounding to ensure whole numbers.
    
    Args:
        branch_data: Dictionary of all branch dataframes
        branch: Branch name to check
        idx: Product index
        existing_withdrawals: Dictionary of withdrawals already made (branch, idx) -> amount
        
    Returns:
        Available surplus quantity (as integer)
    """
    original_surplus = branch_data[branch].iloc[idx]['surplus_quantity']
    already_withdrawn = existing_withdrawals.get((branch, idx), 0.0)
    return math.floor(max(0, original_surplus - already_withdrawn))


def process_single_withdrawal(
    other_branch: str,
    idx: int,
    remaining_needed: float,
    target_amount: float,
    available_surplus: float,
    withdrawals: dict,
    withdrawals_for_row: list
) -> tuple:
    """
    Process a single withdrawal from a surplus branch.
    Uses ceiling rounding for quantities taken.
    
    Args:
        other_branch: Branch providing surplus
        idx: Product index
        remaining_needed: Remaining quantity needed by requesting branch
        target_amount: Maximum target amount to take
        available_surplus: Available surplus in the providing branch
        withdrawals: Dictionary to track all withdrawals
        withdrawals_for_row: List to store withdrawal records for this product
        
    Returns:
        Tuple of (updated remaining_needed, updated target_amount)
    """
    # Calculate amount to take (minimum of remaining_needed, target_amount, available_surplus)
    amount_to_take = math.ceil(min(remaining_needed, target_amount, available_surplus))
    
    if amount_to_take > 0:
        surplus_remaining = math.ceil(max(0, available_surplus - amount_to_take))
        withdrawals_for_row.append({
            'surplus_from_branch': amount_to_take,
            'available_branch': other_branch,
            'surplus_remaining': surplus_remaining,
            'remaining_needed': math.ceil(max(0, remaining_needed - amount_to_take))
        })
        withdrawals[(other_branch, idx)] = withdrawals.get((other_branch, idx), 0.0) + amount_to_take
        remaining_needed = math.ceil(max(0, remaining_needed - amount_to_take))
        target_amount = math.ceil(max(0, target_amount - amount_to_take))
    
    return remaining_needed, target_amount

