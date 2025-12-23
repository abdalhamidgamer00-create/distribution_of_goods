"""Product distribution logic."""
from src.core.domain.calculations.order_calculator import get_needing_branches_order_for_product
from src.services.splitting.processors.surplus_finder import find_surplus_sources_for_single_product
from .analytics import update_analytics_data, merge_withdrawals

def process_all_products(branches: list, branch_data: dict, analytics_data: dict,
                          proportional_allocation: dict, num_products: int) -> tuple:
    """Process all products and return withdrawals data."""
    all_withdrawals, max_withdrawals = {}, 0
    for product_index in range(num_products):
        max_withdrawals = _process_product_needing_branches(
            product_index, branches, branch_data, analytics_data, 
            proportional_allocation, all_withdrawals, max_withdrawals
        )
    return all_withdrawals, max_withdrawals


def _process_product_needing_branches(product_index: int, branches: list, branch_data: dict, analytics_data: dict, 
                                        proportional_allocation: dict, all_withdrawals: dict, max_withdrawals: int) -> int:
    """Process all needing branches for a single product."""
    needing_branches = get_needing_branches_order_for_product(product_index, branch_data, branches)
    for branch in needing_branches:
        max_withdrawals = _process_single_product_for_branch(
            branch, product_index, branch_data, branches, analytics_data, 
            all_withdrawals, proportional_allocation, max_withdrawals
        )
    return max_withdrawals


def _process_single_product_for_branch(branch: str, product_index: int, branch_data: dict, branches: list,
                                        analytics_data: dict, all_withdrawals: dict, 
                                        proportional_allocation: dict, max_withdrawals: int) -> int:
    """Process a single product for a single branch."""
    branch_df = analytics_data[branch][0]
    if branch_df.iloc[product_index]['needed_quantity'] <= 0:
        return max_withdrawals
    
    withdrawals_list, withdrawals = find_surplus_sources_for_single_product(
        branch, product_index, branch_data, branches, all_withdrawals, proportional_allocation
    )
    merge_withdrawals(withdrawals, all_withdrawals)
    return update_analytics_data(branch, product_index, withdrawals_list, analytics_data, max_withdrawals)
