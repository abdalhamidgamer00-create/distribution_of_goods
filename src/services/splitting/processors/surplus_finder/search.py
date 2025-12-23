"""Surplus search logic."""

from src.core.domain.calculations.order_calculator import (
    get_surplus_branches_order_for_product,
)
from src.services.splitting.processors.surplus_helpers import (
    calculate_available_surplus,
    process_single_withdrawal,
)
from src.services.splitting.processors.surplus_finder import records


def init_search_data(
    branch: str, product_index: int, branch_data: dict, branches: list, 
    existing_withdrawals: dict, needed: float
) -> tuple:
    """Initialize search data structures."""
    surplus_search_order = get_surplus_branches_order_for_product(
        product_index, branch, branch_data, branches, existing_withdrawals
    )
    return needed, [], {}, surplus_search_order


def process_surplus_iteration(
    other_branch: str, product_index: int, remaining_needed: float,
    target_amount: float, branch_data: dict, existing_withdrawals: dict,
    withdrawals: dict, withdrawals_for_row: list
) -> tuple:
    """Process one iteration of surplus search."""
    available_surplus = calculate_available_surplus(
        branch_data, other_branch, product_index, existing_withdrawals
    )
    if available_surplus > 0:
        return process_single_withdrawal(
            other_branch, product_index, remaining_needed, target_amount, 
            available_surplus, withdrawals, withdrawals_for_row
        )
    return remaining_needed, target_amount


def execute_surplus_search(
    surplus_search_order: list, product_index: int, remaining_needed: float,
    target_amount: float, branch_data: dict, existing_withdrawals: dict,
    withdrawals: dict, withdrawals_for_row: list
) -> tuple:
    """Execute the search loop and return final values."""
    for other_branch in surplus_search_order:
        if remaining_needed <= 0 or target_amount <= 0:
            break
        remaining_needed, target_amount = process_surplus_iteration(
            other_branch, product_index, remaining_needed, target_amount, 
            branch_data, existing_withdrawals, withdrawals, withdrawals_for_row
        )
    return remaining_needed, target_amount


def search_and_withdraw_surplus(
    branch: str, product_index: int, branch_data: dict, branches: list,
    existing_withdrawals: dict, target_amount: float, needed: float
) -> tuple:
    """Search for surplus in other branches and process withdrawals."""
    remaining_needed, withdrawals_for_row, withdrawals, search_order = init_search_data(
        branch, product_index, branch_data, branches, existing_withdrawals, needed
    )
    
    remaining_needed, _ = execute_surplus_search(
        search_order, product_index, remaining_needed, target_amount, 
        branch_data, existing_withdrawals, withdrawals, withdrawals_for_row
    )
    return withdrawals_for_row, withdrawals, remaining_needed


def search_and_finalize(
    branch: str, product_index: int, branch_data: dict, branches: list,
    existing_withdrawals: dict, target_amount: float, needed: float
) -> tuple:
    """Search for surplus and finalize withdrawals."""
    withdrawals_for_row, withdrawals, remaining_needed = search_and_withdraw_surplus(
        branch, product_index, branch_data, branches, existing_withdrawals, 
        target_amount, needed
    )
    result_list, result_dict = records.finalize_withdrawals(
        withdrawals_for_row, remaining_needed
    )
    return result_list, result_dict if result_dict is not None else withdrawals
