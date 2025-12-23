"""Eligibility logic for branches needing surplus."""
from .tracking import get_branch_product_data, calculate_transferred_amount

def check_branch_needs_transfer(needed: float, current_balance: float, balance_limit: float, 
                                  transferred_so_far: float) -> float:
    """Check if branch needs transfer and calculate remaining capacity. Returns None if not eligible."""
    if needed <= 0 or current_balance >= balance_limit:
        return None
    remaining_needed = needed - transferred_so_far
    if remaining_needed <= 0:
        return None
    return min(remaining_needed, balance_limit - current_balance)


def calculate_branch_eligibility(branch: str, analytics_data: dict, product_index: int, 
                                   balance_limit: float) -> tuple:
    """Calculate if a branch is eligible and its details."""
    balance, needed, avg_sales = get_branch_product_data(analytics_data, branch, product_index)
    transferred_so_far = calculate_transferred_amount(analytics_data, branch, product_index)
    current_balance = balance + transferred_so_far
    remaining_capacity = check_branch_needs_transfer(needed, current_balance, balance_limit, transferred_so_far)
    if remaining_capacity is None:
        return None
    return (branch, avg_sales, current_balance, remaining_capacity)


def find_eligible_branches(branches: list, analytics_data: dict, product_index: int, balance_limit: float) -> list:
    """Find branches eligible for second-round redistribution."""
    eligible = []
    for branch in branches:
        result = calculate_branch_eligibility(branch, analytics_data, product_index, balance_limit)
        if result:
            eligible.append(result)
    
    eligible.sort(key=lambda item: (item[2], -item[1])) # Sort by current_balance ASC, then avg_sales DESC
    return eligible
