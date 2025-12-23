"""Main orchestration for surplus redistribution."""
from time import perf_counter
from src.shared.utils.logging_utils import get_logger
from .eligibility import find_eligible_branches
from .distributor import redistribute_to_branch

logger = get_logger(__name__)

def redistribute_wasted_surplus(branches: list, branch_data: dict, analytics_data: dict,
                                all_withdrawals: dict, max_withdrawals: int, num_products: int,
                                balance_limit: float = 30.0) -> tuple:
    """Redistribute wasted surplus from balance limit rule to other eligible branches."""
    logger.info("Starting second redistribution round for wasted surplus...")
    start_time = perf_counter()
    max_withdrawals, redistributed_count = execute_redistribution(num_products, branches, branch_data, analytics_data, all_withdrawals, max_withdrawals, balance_limit)
    elapsed_time = log_redistribution_result(start_time, redistributed_count)
    return max_withdrawals, elapsed_time


def execute_redistribution(num_products: int, branches: list, branch_data: dict, analytics_data: dict,
                             all_withdrawals: dict, max_withdrawals: int, balance_limit: float) -> tuple:
    """Execute redistribution for all products."""
    redistributed_count = 0
    for product_index in range(num_products):
        max_withdrawals, count = process_single_product(
            product_index, branches, branch_data, analytics_data,
            all_withdrawals, max_withdrawals, balance_limit
        )
        redistributed_count += count
    return max_withdrawals, redistributed_count


def process_single_product(product_index: int, branches: list, branch_data: dict, analytics_data: dict,
                             all_withdrawals: dict, max_withdrawals: int, balance_limit: float) -> tuple:
    """Process redistribution for a single product."""
    redistributed_count = 0
    for branch, _, _, remaining_capacity in find_eligible_branches(branches, analytics_data, product_index, balance_limit):
        max_withdrawals, count = redistribute_to_branch(branch, product_index, remaining_capacity, branches, branch_data, analytics_data, all_withdrawals, max_withdrawals)
        redistributed_count += count
    return max_withdrawals, redistributed_count


def log_redistribution_result(start_time: float, redistributed_count: int) -> float:
    """Log redistribution result and return elapsed time."""
    elapsed_time = perf_counter() - start_time
    logger.info(f"Second redistribution round completed in {elapsed_time:.2f}s ({redistributed_count} transfers)")
    return elapsed_time
