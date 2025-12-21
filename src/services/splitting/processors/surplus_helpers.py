"""Helper functions for surplus calculations"""

import math


def calculate_available_surplus(
    branch_data: dict, 
    branch: str, 
    product_index: int, 
    existing_withdrawals: dict
) -> float:
    """
    Calculate available surplus for a product after accounting for withdrawals.
    Uses floor rounding to ensure whole numbers.
    
    Args:
        branch_data: Dictionary of all branch dataframes
        branch: Branch name to check
        product_index: Product index to check
        existing_withdrawals: Dictionary of withdrawals already made (branch, product_index) -> amount
        
    Returns:
        Available surplus quantity (as integer)
    """
    original_surplus = branch_data[branch].iloc[product_index]['surplus_quantity']
    already_withdrawn = existing_withdrawals.get((branch, product_index), 0.0)
    return math.floor(max(0, original_surplus - already_withdrawn))


def _calculate_withdrawal_amounts(remaining_needed: float, target_amount: float, available_surplus: float) -> int:
    """Calculate the amount to withdraw."""
    return math.ceil(min(remaining_needed, target_amount, available_surplus))


def _record_withdrawal(other_branch: str, product_index: int, amount: int, available_surplus: float, 
                       remaining_needed: float, withdrawals: dict, withdrawals_for_row: list) -> None:
    """Record a withdrawal in the tracking structures."""
    surplus_remaining = math.ceil(max(0, available_surplus - amount))
    new_remaining = math.ceil(max(0, remaining_needed - amount))
    
    withdrawals_for_row.append({
        'surplus_from_branch': amount,
        'available_branch': other_branch,
        'surplus_remaining': surplus_remaining,
        'remaining_needed': new_remaining
    })
    withdrawals[(other_branch, product_index)] = withdrawals.get((other_branch, product_index), 0.0) + amount


def process_single_withdrawal(
    other_branch: str,
    product_index: int,
    remaining_needed: float,
    target_amount: float,
    available_surplus: float,
    withdrawals: dict,
    withdrawals_for_row: list
) -> tuple:
    """Process a single withdrawal from a surplus branch."""
    amount_to_take = _calculate_withdrawal_amounts(remaining_needed, target_amount, available_surplus)
    
    if amount_to_take > 0:
        _record_withdrawal(other_branch, product_index, amount_to_take, available_surplus, 
                          remaining_needed, withdrawals, withdrawals_for_row)
        remaining_needed = math.ceil(max(0, remaining_needed - amount_to_take))
        target_amount = math.ceil(max(0, target_amount - amount_to_take))
    
    return remaining_needed, target_amount


