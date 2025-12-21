"""Surplus redistribution - Second round allocation for wasted surplus"""

from time import perf_counter
from src.core.domain.calculations.order_calculator import get_needing_branches_order_for_product
from src.services.splitting.processors.surplus_helpers import calculate_available_surplus
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _calculate_transferred_amount(analytics_data: dict, branch: str, product_idx: int) -> float:
    """Calculate total amount already transferred to a branch for a product."""
    withdrawals_list = analytics_data[branch][1]
    if product_idx >= len(withdrawals_list):
        return 0.0
    
    return sum(w.get('surplus_from_branch', 0.0) for w in withdrawals_list[product_idx])


def _find_eligible_branches(
    branches: list,
    analytics_data: dict,
    product_idx: int,
    balance_limit: float
) -> list:
    """Find branches eligible for second-round redistribution."""
    eligible = []
    
    for branch in branches:
        branch_df = analytics_data[branch][0]
        balance = branch_df.iloc[product_idx]['balance']
        needed = branch_df.iloc[product_idx]['needed_quantity']
        
        transferred_so_far = _calculate_transferred_amount(analytics_data, branch, product_idx)
        current_balance = balance + transferred_so_far
        
        if needed <= 0 or current_balance >= balance_limit:
            continue
        
        remaining_needed = needed - transferred_so_far
        if remaining_needed <= 0:
            continue
        
        remaining_capacity = min(remaining_needed, balance_limit - current_balance)
        avg_sales = branch_df.iloc[product_idx]['avg_sales']
        eligible.append((branch, avg_sales, current_balance, remaining_capacity))
    
    # Sort by priority: lowest balance first, then highest avg_sales
    eligible.sort(key=lambda x: (x[2], -x[1]))
    return eligible


def _record_redistribution(branch: str, other_branch: str, product_idx: int, transfer_amount: float,
                           available_surplus: float, analytics_data: dict, all_withdrawals: dict,
                           max_withdrawals: int) -> int:
    """Record a redistribution in the tracking structures."""
    key = (other_branch, product_idx)
    all_withdrawals[key] = all_withdrawals.get(key, 0.0) + transfer_amount
    
    withdrawals_list = analytics_data[branch][1]
    if product_idx < len(withdrawals_list):
        withdrawals_list[product_idx].append({
            'surplus_from_branch': transfer_amount,
            'available_branch': other_branch,
            'surplus_remaining': available_surplus - transfer_amount,
            'remaining_needed': 0.0
        })
        max_withdrawals = max(max_withdrawals, len(withdrawals_list[product_idx]))
    
    return max_withdrawals


def _try_redistribute_from_branch(other_branch: str, branch: str, product_idx: int, remaining_capacity: float,
                                   branch_data: dict, analytics_data: dict, all_withdrawals: dict,
                                   max_withdrawals: int) -> tuple:
    """Try to redistribute from a single source branch."""
    available_surplus = calculate_available_surplus(
        branch_data, other_branch, product_idx, all_withdrawals
    )
    
    if available_surplus <= 0:
        return max_withdrawals, 0, remaining_capacity
    
    transfer_amount = min(available_surplus, remaining_capacity)
    if transfer_amount <= 0:
        return max_withdrawals, 0, remaining_capacity
    
    max_withdrawals = _record_redistribution(
        branch, other_branch, product_idx, transfer_amount,
        available_surplus, analytics_data, all_withdrawals, max_withdrawals
    )
    
    logger.debug(
        f"Second round: Transferred {transfer_amount:.2f} of product {product_idx} "
        f"from {other_branch} to {branch}"
    )
    
    return max_withdrawals, 1, remaining_capacity - transfer_amount


def _redistribute_to_branch(
    branch: str,
    product_idx: int,
    remaining_capacity: float,
    branches: list,
    branch_data: dict,
    analytics_data: dict,
    all_withdrawals: dict,
    max_withdrawals: int
) -> tuple:
    """Attempt to redistribute surplus to a single branch."""
    redistributed_count = 0
    
    for other_branch in branches:
        if other_branch == branch or remaining_capacity <= 0:
            continue
        
        max_withdrawals, count, remaining_capacity = _try_redistribute_from_branch(
            other_branch, branch, product_idx, remaining_capacity,
            branch_data, analytics_data, all_withdrawals, max_withdrawals
        )
        redistributed_count += count
    
    return max_withdrawals, redistributed_count


def _process_single_product(product_idx: int, branches: list, branch_data: dict, analytics_data: dict,
                             all_withdrawals: dict, max_withdrawals: int, balance_limit: float) -> tuple:
    """Process redistribution for a single product."""
    redistributed_count = 0
    eligible_branches = _find_eligible_branches(branches, analytics_data, product_idx, balance_limit)
    
    for branch, _, _, remaining_capacity in eligible_branches:
        max_withdrawals, count = _redistribute_to_branch(
            branch, product_idx, remaining_capacity, branches,
            branch_data, analytics_data, all_withdrawals, max_withdrawals
        )
        redistributed_count += count
    
    return max_withdrawals, redistributed_count


def redistribute_wasted_surplus(
    branches: list,
    branch_data: dict,
    analytics_data: dict,
    all_withdrawals: dict,
    max_withdrawals: int,
    num_products: int,
    balance_limit: float = 30.0
) -> tuple:
    """Redistribute wasted surplus from balance limit rule to other eligible branches."""
    logger.info("Starting second redistribution round for wasted surplus...")
    start_time = perf_counter()
    redistributed_count = 0
    
    for product_idx in range(num_products):
        max_withdrawals, count = _process_single_product(
            product_idx, branches, branch_data, analytics_data,
            all_withdrawals, max_withdrawals, balance_limit
        )
        redistributed_count += count
    
    elapsed_time = perf_counter() - start_time
    logger.info(f"Second redistribution round completed in {elapsed_time:.2f}s ({redistributed_count} transfers)")
    
    return max_withdrawals, elapsed_time

