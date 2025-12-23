"""Main orchestration logic for surplus finder."""

from src.services.splitting.processors.target_calculator import (
    calculate_target_amount,
    should_skip_transfer,
)
from src.services.splitting.processors.surplus_finder import records, data, search


def check_early_returns(needed: float, balance: float) -> tuple:
    """Check early return conditions, return (should_return, list, dict)."""
    if needed <= 0:
        return True, [records.create_empty_withdrawal_record()], {}
    
    if should_skip_transfer(balance):
        return True, [records.create_empty_withdrawal_record(needed)], {}
    
    return False, None, None


def handle_target_and_search(
    branch: str, product_index: int, branch_data: dict, branches: list,
    existing_withdrawals: dict, proportional_allocation: dict, 
    needed: float, balance: float
) -> tuple:
    """Handle target calculation and surplus search."""
    allocated = data.get_allocated_amount(
        product_index, branch, proportional_allocation
    )
    target_amount = calculate_target_amount(needed, balance, allocated)
    
    if target_amount <= 0:
        return [records.create_empty_withdrawal_record(needed)], {}
    
    return search.search_and_finalize(
        branch, product_index, branch_data, branches, existing_withdrawals, 
        target_amount, needed
    )


def find_surplus_sources_for_single_product(
    branch: str, product_index: int, branch_data: dict, branches: list,
    existing_withdrawals: dict = None, proportional_allocation: dict = None
) -> tuple:
    """Find surplus sources for a single product for a specific branch."""
    existing_withdrawals = existing_withdrawals or {}
    proportional_allocation = proportional_allocation or {}
    
    needed, balance = data.get_product_data(branch_data, branch, product_index)
    
    should_return, result_list, result_dict = check_early_returns(needed, balance)
    if should_return:
        return result_list, result_dict
    
    return handle_target_and_search(
        branch, product_index, branch_data, branches, existing_withdrawals, 
        proportional_allocation, needed, balance
    )
