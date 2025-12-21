"""Find surplus sources for branches needing products"""

import math
from src.core.domain.calculations.order_calculator import (
    get_surplus_branches_order_for_product,
)
from src.services.splitting.processors.surplus_helpers import (
    calculate_available_surplus,
    process_single_withdrawal,
)
from src.services.splitting.processors.target_calculator import (
    calculate_target_amount,
    should_skip_transfer,
)


def _create_empty_withdrawal_record(remaining_needed: float = 0.0) -> dict:
    """Create a standard empty withdrawal record."""
    return {
        'surplus_from_branch': 0.0,
        'available_branch': '',
        'surplus_remaining': 0.0,
        'remaining_needed': math.ceil(remaining_needed) if remaining_needed > 0 else 0.0
    }


def _get_allocated_amount(
    product_index: int,
    branch: str,
    proportional_allocation: dict
) -> float:
    """Extract allocated amount from proportional allocation dictionary."""
    if product_index not in proportional_allocation:
        return None
    if branch not in proportional_allocation[product_index]:
        return None
    return proportional_allocation[product_index][branch]


def _search_and_withdraw_surplus(
    branch: str,
    product_index: int,
    branch_data: dict,
    branches: list,
    existing_withdrawals: dict,
    target_amount: float,
    needed: float
) -> tuple:
    """
    Search for surplus in other branches and process withdrawals.
    
    Returns:
        Tuple of (withdrawals_for_row list, withdrawals dict, remaining_needed)
    """
    remaining_needed = needed
    withdrawals_for_row = []
    withdrawals = {}
    
    surplus_search_order = get_surplus_branches_order_for_product(
        product_index, branch, branch_data, branches, existing_withdrawals
    )
    
    for other_branch in surplus_search_order:
        if remaining_needed <= 0 or target_amount <= 0:
            break
        
        available_surplus = calculate_available_surplus(
            branch_data, other_branch, product_index, existing_withdrawals
        )
        
        if available_surplus > 0:
            remaining_needed, target_amount = process_single_withdrawal(
                other_branch, product_index, remaining_needed, target_amount,
                available_surplus, withdrawals, withdrawals_for_row
            )
    
    return withdrawals_for_row, withdrawals, remaining_needed


def _check_early_returns(needed: float, balance: float) -> tuple:
    """Check early return conditions, return (should_return, withdrawal_record)."""
    if needed <= 0:
        return True, [_create_empty_withdrawal_record()], {}
    
    if should_skip_transfer(balance):
        return True, [_create_empty_withdrawal_record(needed)], {}
    
    return False, None, None


def _finalize_withdrawals(withdrawals_for_row: list, remaining_needed: float) -> tuple:
    """Finalize withdrawal results."""
    if not withdrawals_for_row:
        return [_create_empty_withdrawal_record(remaining_needed)], {}
    
    withdrawals_for_row[-1]['remaining_needed'] = math.ceil(remaining_needed)
    return withdrawals_for_row, None  # None signals to use existing withdrawals


def find_surplus_sources_for_single_product(
    branch: str,
    product_idx: int,
    branch_data: dict,
    branches: list,
    existing_withdrawals: dict = None,
    proportional_allocation: dict = None
) -> tuple:
    """Find surplus sources for a single product for a specific branch."""
    if existing_withdrawals is None:
        existing_withdrawals = {}
    if proportional_allocation is None:
        proportional_allocation = {}
    
    branch_df = branch_data[branch]
    needed = branch_df.iloc[product_idx]['needed_quantity']
    balance = branch_df.iloc[product_idx]['balance']
    
    should_return, result_list, result_dict = _check_early_returns(needed, balance)
    if should_return:
        return result_list, result_dict
    
    allocated = _get_allocated_amount(product_idx, branch, proportional_allocation)
    target_amount = calculate_target_amount(needed, balance, allocated)
    
    if target_amount <= 0:
        return [_create_empty_withdrawal_record(needed)], {}
    
    withdrawals_for_row, withdrawals, remaining_needed = _search_and_withdraw_surplus(
        branch, product_idx, branch_data, branches, existing_withdrawals, target_amount, needed
    )
    
    result_list, result_dict = _finalize_withdrawals(withdrawals_for_row, remaining_needed)
    return result_list, result_dict if result_dict is not None else withdrawals

