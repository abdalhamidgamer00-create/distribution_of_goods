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


def find_surplus_sources_for_single_product(
    branch: str,
    product_idx: int,
    branch_data: dict,
    branches: list,
    existing_withdrawals: dict = None,
    proportional_allocation: dict = None
) -> tuple:
    """
    Find surplus sources for a single product for a specific branch.
    
    This function:
    1. Checks if branch needs the product
    2. Applies balance rules (no transfer if balance >= 30)
    3. Calculates target amount based on rules
    4. Searches for surplus in other branches
    5. Processes withdrawals
    
    Args:
        branch: Current branch name (receiving branch)
        product_idx: Product index to process
        branch_data: Dictionary of all branch dataframes
        branches: List of all branch names
        existing_withdrawals: Dictionary of withdrawals already made
        proportional_allocation: Dictionary mapping product_idx to allocated amounts
        
    Returns:
        Tuple of (withdrawals_list, withdrawals_dict)
        - withdrawals_list: List of withdrawal records for analytics
        - withdrawals_dict: Dictionary tracking all withdrawals
    """
    if existing_withdrawals is None:
        existing_withdrawals = {}
    if proportional_allocation is None:
        proportional_allocation = {}
    
    branch_df = branch_data[branch]
    needed = branch_df.iloc[product_idx]['needed_quantity']
    balance = branch_df.iloc[product_idx]['balance']
    
    # Early return if no need
    if needed <= 0:
        return [{
            'surplus_from_branch': 0.0,
            'available_branch': '',
            'surplus_remaining': 0.0,
            'remaining_needed': 0.0
        }], {}
    
    # Apply rule: No transfer if balance >= 30
    if should_skip_transfer(balance):
        return [{
            'surplus_from_branch': 0.0,
            'available_branch': '',
            'surplus_remaining': 0.0,
            'remaining_needed': math.ceil(needed)  # Original needed amount
        }], {}
    
    # Get proportional allocation if exists
    allocated = None
    if product_idx in proportional_allocation:
        if branch in proportional_allocation[product_idx]:
            allocated = proportional_allocation[product_idx][branch]
    
    # Calculate target amount based on rules
    target_amount = calculate_target_amount(needed, balance, allocated)
    
    # If target_amount is 0, no transfer needed
    if target_amount <= 0:
        return [{
            'surplus_from_branch': 0.0,
            'available_branch': '',
            'surplus_remaining': 0.0,
            'remaining_needed': math.ceil(needed)
        }], {}
    
    # Initialize tracking variables
    remaining_needed = needed
    withdrawals_for_row = []
    withdrawals = {}
    
    # Get order of branches to search for surplus
    surplus_search_order = get_surplus_branches_order_for_product(
        product_idx, branch, branch_data, branches, existing_withdrawals
    )
    
    # Search for surplus in other branches
    for other_branch in surplus_search_order:
        if remaining_needed <= 0 or target_amount <= 0:
            break
        
        available_surplus = calculate_available_surplus(
            branch_data, other_branch, product_idx, existing_withdrawals
        )
        
        if available_surplus > 0:
            remaining_needed, target_amount = process_single_withdrawal(
                other_branch, product_idx, remaining_needed, target_amount,
                available_surplus, withdrawals, withdrawals_for_row
            )
    
    # Add empty record if no withdrawals were made
    if not withdrawals_for_row:
        withdrawals_for_row.append({
            'surplus_from_branch': 0.0,
            'available_branch': '',
            'surplus_remaining': 0.0,
            'remaining_needed': math.ceil(remaining_needed)
        })
    else:
        # Update last record with final remaining_needed
        withdrawals_for_row[-1]['remaining_needed'] = math.ceil(remaining_needed)
    
    return withdrawals_for_row, withdrawals
