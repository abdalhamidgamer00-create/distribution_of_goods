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


# =============================================================================
# PUBLIC API
# =============================================================================

def find_surplus_sources_for_single_product(branch: str, product_index: int, branch_data: dict, branches: list,
                                            existing_withdrawals: dict = None, proportional_allocation: dict = None) -> tuple:
    """Find surplus sources for a single product for a specific branch."""
    existing_withdrawals, proportional_allocation = existing_withdrawals or {}, proportional_allocation or {}
    needed, balance = _get_product_data(branch_data, branch, product_index)
    
    should_return, result_list, result_dict = _check_early_returns(needed, balance)
    if should_return:
        return result_list, result_dict
    
    return _handle_target_and_search(branch, product_index, branch_data, branches, existing_withdrawals, proportional_allocation, needed, balance)


# =============================================================================
# WITHDRAWAL RECORD HELPERS
# =============================================================================

def _create_empty_withdrawal_record(remaining_needed: float = 0.0) -> dict:
    """Create a standard empty withdrawal record."""
    return {
        'surplus_from_branch': 0.0,
        'available_branch': '',
        'surplus_remaining': 0.0,
        'remaining_needed': math.ceil(remaining_needed) if remaining_needed > 0 else 0.0
    }


def _finalize_withdrawals(withdrawals_for_row: list, remaining_needed: float) -> tuple:
    """Finalize withdrawal results."""
    if not withdrawals_for_row:
        return [_create_empty_withdrawal_record(remaining_needed)], {}
    
    withdrawals_for_row[-1]['remaining_needed'] = math.ceil(remaining_needed)
    return withdrawals_for_row, None  # None signals to use existing withdrawals


# =============================================================================
# PRODUCT DATA HELPERS
# =============================================================================

def _get_product_data(branch_data: dict, branch: str, product_index: int) -> tuple:
    """Get needed and balance for a product."""
    branch_dataframe = branch_data[branch]
    return branch_dataframe.iloc[product_index]['needed_quantity'], branch_dataframe.iloc[product_index]['balance']


def _get_allocated_amount(product_index: int, branch: str, proportional_allocation: dict) -> float:
    """Extract allocated amount from proportional allocation dictionary."""
    if product_index not in proportional_allocation:
        return None
    if branch not in proportional_allocation[product_index]:
        return None
    return proportional_allocation[product_index][branch]


# =============================================================================
# EARLY EXIT HELPERS
# =============================================================================

def _check_early_returns(needed: float, balance: float) -> tuple:
    """Check early return conditions, return (should_return, withdrawal_record)."""
    if needed <= 0:
        return True, [_create_empty_withdrawal_record()], {}
    
    if should_skip_transfer(balance):
        return True, [_create_empty_withdrawal_record(needed)], {}
    
    return False, None, None


# =============================================================================
# SURPLUS SEARCH HELPERS
# =============================================================================

def _init_search_data(branch: str, product_index: int, branch_data: dict, branches: list, 
                       existing_withdrawals: dict, needed: float) -> tuple:
    """Initialize search data structures."""
    surplus_search_order = get_surplus_branches_order_for_product(product_index, branch, branch_data, branches, existing_withdrawals)
    return needed, [], {}, surplus_search_order


def _process_surplus_iteration(other_branch: str, product_index: int, remaining_needed: float,
                                target_amount: float, branch_data: dict, existing_withdrawals: dict,
                                withdrawals: dict, withdrawals_for_row: list) -> tuple:
    """Process one iteration of surplus search."""
    available_surplus = calculate_available_surplus(branch_data, other_branch, product_index, existing_withdrawals)
    if available_surplus > 0:
        return process_single_withdrawal(other_branch, product_index, remaining_needed, target_amount, available_surplus, withdrawals, withdrawals_for_row)
    return remaining_needed, target_amount


def _execute_surplus_search(surplus_search_order: list, product_index: int, remaining_needed: float,
                             target_amount: float, branch_data: dict, existing_withdrawals: dict,
                             withdrawals: dict, withdrawals_for_row: list) -> tuple:
    """Execute the search loop and return final values."""
    for other_branch in surplus_search_order:
        if remaining_needed <= 0 or target_amount <= 0:
            break
        remaining_needed, target_amount = _process_surplus_iteration(
            other_branch, product_index, remaining_needed, target_amount, 
            branch_data, existing_withdrawals, withdrawals, withdrawals_for_row
        )
    return remaining_needed, target_amount


# =============================================================================
# WITHDRAWAL PROCESSING HELPERS
# =============================================================================

def _search_and_withdraw_surplus(branch: str, product_index: int, branch_data: dict, branches: list,
                                 existing_withdrawals: dict, target_amount: float, needed: float) -> tuple:
    """Search for surplus in other branches and process withdrawals."""
    remaining_needed, withdrawals_for_row, withdrawals, surplus_search_order = _init_search_data(
        branch, product_index, branch_data, branches, existing_withdrawals, needed
    )
    
    remaining_needed, _ = _execute_surplus_search(
        surplus_search_order, product_index, remaining_needed, target_amount, 
        branch_data, existing_withdrawals, withdrawals, withdrawals_for_row
    )
    return withdrawals_for_row, withdrawals, remaining_needed


def _search_and_finalize(branch: str, product_index: int, branch_data: dict, branches: list,
                          existing_withdrawals: dict, target_amount: float, needed: float) -> tuple:
    """Search for surplus and finalize withdrawals."""
    withdrawals_for_row, withdrawals, remaining_needed = _search_and_withdraw_surplus(
        branch, product_index, branch_data, branches, existing_withdrawals, target_amount, needed
    )
    result_list, result_dict = _finalize_withdrawals(withdrawals_for_row, remaining_needed)
    return result_list, result_dict if result_dict is not None else withdrawals


def _handle_target_and_search(branch: str, product_index: int, branch_data: dict, branches: list,
                               existing_withdrawals: dict, proportional_allocation: dict, 
                               needed: float, balance: float) -> tuple:
    """Handle target calculation and surplus search."""
    allocated = _get_allocated_amount(product_index, branch, proportional_allocation)
    target_amount = calculate_target_amount(needed, balance, allocated)
    
    if target_amount <= 0:
        return [_create_empty_withdrawal_record(needed)], {}
    
    return _search_and_finalize(branch, product_index, branch_data, branches, existing_withdrawals, target_amount, needed)
