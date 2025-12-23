"""Eligibility logic for branches needing surplus."""
from .tracking import get_branch_product_data, calculate_transferred_amount

def check_branch_needs_transfer(
    needed: float, current_balance: float, balance_limit: float, 
    transferred_so_far: float
) -> float:
    """Check if branch needs transfer and calculate remaining capacity.
    
    Returns:
        float: Remaining capacity if eligible, None otherwise.
    """
    if needed <= 0 or current_balance >= balance_limit:
        return None
    remaining_needed = needed - transferred_so_far
    if remaining_needed <= 0:
        return None
    return min(remaining_needed, balance_limit - current_balance)


def calculate_branch_eligibility(
    branch: str, analytics_data: dict, product_index: int, 
    balance_limit: float
) -> tuple:
    """Calculate if a branch is eligible and its details."""
    data = get_branch_product_data(analytics_data, branch, product_index)
    balance, needed, avg_sales = data
    
    transferred = calculate_transferred_amount(
        analytics_data, branch, product_index
    )
    current_balance = balance + transferred
    
    capacity = check_branch_needs_transfer(
        needed, current_balance, balance_limit, transferred
    )
    if capacity is None:
        return None
    return (branch, avg_sales, current_balance, capacity)


def find_eligible_branches(
    branches: list, analytics_data: dict, product_index: int, 
    balance_limit: float
) -> list:
    """Find branches eligible for second-round redistribution."""
    eligible = []
    for branch in branches:
        result = calculate_branch_eligibility(
            branch, analytics_data, product_index, balance_limit
        )
        if result:
            eligible.append(result)
    
    # Sort by current_balance ASC, then avg_sales DESC
    eligible.sort(key=lambda item: (item[2], -item[1])) 
    return eligible
