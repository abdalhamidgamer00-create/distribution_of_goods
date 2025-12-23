"""Helper functions for surplus calculations"""

import math


# =============================================================================
# PUBLIC API
# =============================================================================

def calculate_available_surplus(
    branch_data: dict, branch: str, product_index: int, 
    existing_withdrawals: dict
) -> float:
    """Calculate available surplus after accounting for withdrawals."""
    original_surplus = _get_original_surplus(branch_data, branch, product_index)
    already_withdrawn = existing_withdrawals.get((branch, product_index), 0.0)
    return math.floor(max(0, original_surplus - already_withdrawn))


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
    amount_to_take = _calculate_withdrawal_amounts(
        remaining_needed, target_amount, available_surplus
    )
    
    if amount_to_take > 0:
        return _execute_withdrawal(
            other_branch, 
            product_index, 
            amount_to_take, 
            available_surplus,
            remaining_needed, 
            target_amount, 
            withdrawals, 
            withdrawals_for_row
        )
    return remaining_needed, target_amount


# =============================================================================
# SURPLUS RETRIEVAL HELPERS
# =============================================================================

def _get_original_surplus(
    branch_data: dict, branch: str, product_index: int
) -> float:
    """Get original surplus quantity for a product from branch data."""
    return branch_data[branch].iloc[product_index]['surplus_quantity']


# =============================================================================
# WITHDRAWAL CALCULATION HELPERS
# =============================================================================

def _calculate_withdrawal_amounts(
    remaining_needed: float, target_amount: float, available_surplus: float
) -> int:
    """Calculate the amount to withdraw."""
    vals = [remaining_needed, target_amount, available_surplus]
    return math.ceil(min(vals))


def _update_amounts(
    remaining_needed: float, target_amount: float, amount_taken: float
) -> tuple:
    """Update remaining and target amounts after withdrawal."""
    new_needed = math.ceil(max(0, remaining_needed - amount_taken))
    new_target = math.ceil(max(0, target_amount - amount_taken))
    return new_needed, new_target


# =============================================================================
# WITHDRAWAL RECORDING HELPERS
# =============================================================================

def _record_withdrawal(
    other_branch: str, 
    product_index: int, 
    amount: int, 
    available_surplus: float, 
    remaining_needed: float, 
    withdrawals: dict, 
    withdrawals_for_row: list
) -> None:
    """Record a withdrawal in the tracking structures."""
    surplus_rem = math.ceil(max(0, available_surplus - amount))
    new_rem_needed = math.ceil(max(0, remaining_needed - amount))
    withdrawals_for_row.append({
        'surplus_from_branch': amount, 
        'available_branch': other_branch, 
        'surplus_remaining': surplus_rem, 
        'remaining_needed': new_rem_needed
    })
    
    key = (other_branch, product_index)
    withdrawals[key] = withdrawals.get(key, 0.0) + amount


def _execute_withdrawal(
    other_branch: str, 
    product_index: int, 
    amount_to_take: int, 
    available_surplus: float, 
    remaining_needed: float, 
    target_amount: float,
    withdrawals: dict, 
    withdrawals_for_row: list
) -> tuple:
    """Execute withdrawal and return updated amounts."""
    _record_withdrawal(
        other_branch, 
        product_index, 
        amount_to_take, 
        available_surplus, 
        remaining_needed, 
        withdrawals, 
        withdrawals_for_row
    )
    return _update_amounts(remaining_needed, target_amount, amount_to_take)
