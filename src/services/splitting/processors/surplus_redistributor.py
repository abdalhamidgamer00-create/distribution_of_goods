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


def _check_branch_needs_transfer(needed: float, current_balance: float, balance_limit: float, 
                                  transferred_so_far: float) -> tuple:
    """Check if branch needs transfer and calculate remaining capacity."""
    if needed <= 0 or current_balance >= balance_limit:
        return None
    remaining_needed = needed - transferred_so_far
    if remaining_needed <= 0:
        return None
    return min(remaining_needed, balance_limit - current_balance)


def _get_branch_product_data(analytics_data: dict, branch: str, product_idx: int) -> tuple:
    """Get branch product data (balance, needed, avg_sales)."""
    branch_df = analytics_data[branch][0]
    return (branch_df.iloc[product_idx]['balance'], branch_df.iloc[product_idx]['needed_quantity'], 
            branch_df.iloc[product_idx]['avg_sales'])


def _calculate_branch_eligibility(branch: str, analytics_data: dict, product_idx: int, 
                                   balance_limit: float) -> tuple:
    """Calculate if a branch is eligible and its details."""
    balance, needed, avg_sales = _get_branch_product_data(analytics_data, branch, product_idx)
    transferred_so_far = _calculate_transferred_amount(analytics_data, branch, product_idx)
    current_balance = balance + transferred_so_far
    
    remaining_capacity = _check_branch_needs_transfer(needed, current_balance, balance_limit, transferred_so_far)
    if remaining_capacity is None:
        return None
    
    return (branch, avg_sales, current_balance, remaining_capacity)


def _find_eligible_branches(branches: list, analytics_data: dict, product_idx: int, balance_limit: float) -> list:
    """Find branches eligible for second-round redistribution."""
    eligible = []
    for branch in branches:
        result = _calculate_branch_eligibility(branch, analytics_data, product_idx, balance_limit)
        if result:
            eligible.append(result)
    
    eligible.sort(key=lambda x: (x[2], -x[1]))
    return eligible


def _append_withdrawal(withdrawals_list: list, product_idx: int, transfer_amount: float, 
                        other_branch: str, available_surplus: float) -> int:
    """Append withdrawal entry and return max withdrawals count."""
    if product_idx < len(withdrawals_list):
        withdrawals_list[product_idx].append({
            'surplus_from_branch': transfer_amount,
            'available_branch': other_branch,
            'surplus_remaining': available_surplus - transfer_amount,
            'remaining_needed': 0.0
        })
        return len(withdrawals_list[product_idx])
    return 0


def _record_redistribution(branch: str, other_branch: str, product_idx: int, transfer_amount: float,
                           available_surplus: float, analytics_data: dict, all_withdrawals: dict,
                           max_withdrawals: int) -> int:
    """Record a redistribution in the tracking structures."""
    key = (other_branch, product_idx)
    all_withdrawals[key] = all_withdrawals.get(key, 0.0) + transfer_amount
    
    count = _append_withdrawal(analytics_data[branch][1], product_idx, transfer_amount, other_branch, available_surplus)
    return max(max_withdrawals, count)


def _execute_transfer(branch: str, other_branch: str, product_idx: int, transfer_amount: float,
                      available_surplus: float, remaining_capacity: float, analytics_data: dict,
                      all_withdrawals: dict, max_withdrawals: int) -> tuple:
    """Execute a redistribution transfer."""
    max_withdrawals = _record_redistribution(
        branch, other_branch, product_idx, transfer_amount,
        available_surplus, analytics_data, all_withdrawals, max_withdrawals
    )
    
    logger.debug(f"Second round: Transferred {transfer_amount:.2f} of product {product_idx} from {other_branch} to {branch}")
    return max_withdrawals, 1, remaining_capacity - transfer_amount


def _try_redistribute_from_branch(other_branch: str, branch: str, product_idx: int, remaining_capacity: float,
                                   branch_data: dict, analytics_data: dict, all_withdrawals: dict,
                                   max_withdrawals: int) -> tuple:
    """Try to redistribute from a single source branch."""
    available_surplus = calculate_available_surplus(branch_data, other_branch, product_idx, all_withdrawals)
    
    if available_surplus <= 0:
        return max_withdrawals, 0, remaining_capacity
    
    transfer_amount = min(available_surplus, remaining_capacity)
    if transfer_amount <= 0:
        return max_withdrawals, 0, remaining_capacity
    
    return _execute_transfer(branch, other_branch, product_idx, transfer_amount, 
                             available_surplus, remaining_capacity, analytics_data, all_withdrawals, max_withdrawals)


def _process_all_other_branches(branch: str, product_idx: int, remaining_capacity: float, branches: list,
                                 branch_data: dict, analytics_data: dict, all_withdrawals: dict,
                                 max_withdrawals: int) -> tuple:
    """Process redistribution from all other branches."""
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


def _redistribute_to_branch(branch: str, product_idx: int, remaining_capacity: float, branches: list,
                            branch_data: dict, analytics_data: dict, all_withdrawals: dict,
                            max_withdrawals: int) -> tuple:
    """Attempt to redistribute surplus to a single branch."""
    return _process_all_other_branches(branch, product_idx, remaining_capacity, branches,
                                       branch_data, analytics_data, all_withdrawals, max_withdrawals)


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


def _execute_redistribution(num_products: int, branches: list, branch_data: dict, analytics_data: dict,
                             all_withdrawals: dict, max_withdrawals: int, balance_limit: float) -> tuple:
    """Execute redistribution for all products."""
    redistributed_count = 0
    for product_idx in range(num_products):
        max_withdrawals, count = _process_single_product(
            product_idx, branches, branch_data, analytics_data,
            all_withdrawals, max_withdrawals, balance_limit
        )
        redistributed_count += count
    return max_withdrawals, redistributed_count


def redistribute_wasted_surplus(branches: list, branch_data: dict, analytics_data: dict,
                                all_withdrawals: dict, max_withdrawals: int, num_products: int,
                                balance_limit: float = 30.0) -> tuple:
    """Redistribute wasted surplus from balance limit rule to other eligible branches."""
    logger.info("Starting second redistribution round for wasted surplus...")
    start_time = perf_counter()
    
    max_withdrawals, redistributed_count = _execute_redistribution(
        num_products, branches, branch_data, analytics_data, all_withdrawals, max_withdrawals, balance_limit
    )
    
    elapsed_time = perf_counter() - start_time
    logger.info(f"Second redistribution round completed in {elapsed_time:.2f}s ({redistributed_count} transfers)")
    
    return max_withdrawals, elapsed_time

