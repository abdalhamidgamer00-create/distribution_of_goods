"""Distribution execution logic."""
from src.shared.utils.logging_utils import get_logger
from src.services.splitting.processors.surplus_helpers import (
    calculate_available_surplus
)
from .availability import (
    check_surplus_availability, 
    should_skip_branch
)
from .tracking import record_redistribution

logger = get_logger(__name__)

def execute_transfer(
    branch: str, 
    other_branch: str, 
    product_index: int, 
    transfer_amount: float,
    available_surplus: float, 
    remaining_capacity: float, 
    analytics_data: dict,
    all_withdrawals: dict, 
    max_withdrawals: int
) -> tuple:
    """Execute a redistribution transfer."""
    max_withdrawals = record_redistribution(
        branch, 
        other_branch, 
        product_index, 
        transfer_amount,
        available_surplus, 
        analytics_data, 
        all_withdrawals, 
        max_withdrawals
    )
    
    msg = (
        f"Second round: Transferred {transfer_amount:.2f} of product "
        f"{product_index} from {other_branch} to {branch}"
    )
    logger.debug(msg)
    return max_withdrawals, 1, remaining_capacity - transfer_amount


def try_redistribute_from_branch(
    other_branch: str, 
    branch: str, 
    product_index: int, 
    remaining_capacity: float,
    branch_data: dict, 
    analytics_data: dict, 
    all_withdrawals: dict,
    max_withdrawals: int
) -> tuple:
    """Try to redistribute from a single source branch."""
    available_surplus = calculate_available_surplus(
        branch_data, other_branch, product_index, all_withdrawals
    )
    transfer_amount = check_surplus_availability(
        branch_data, other_branch, product_index, 
        all_withdrawals, remaining_capacity
    )
    
    if transfer_amount <= 0:
        return max_withdrawals, 0, remaining_capacity
    
    return execute_transfer(
        branch, 
        other_branch, 
        product_index, 
        transfer_amount, 
        available_surplus, 
        remaining_capacity, 
        analytics_data, 
        all_withdrawals, 
        max_withdrawals
    )


def process_all_other_branches(
    branch: str, 
    product_index: int, 
    remaining_capacity: float, 
    branches: list,
    branch_data: dict, 
    analytics_data: dict, 
    all_withdrawals: dict,
    max_withdrawals: int
) -> tuple:
    """Process redistribution from all other branches."""
    redistributed_count = 0
    for other_branch in branches:
        if not should_skip_branch(other_branch, branch, remaining_capacity):
            res = try_redistribute_from_branch(
                other_branch, 
                branch, 
                product_index, 
                remaining_capacity, 
                branch_data, 
                analytics_data, 
                all_withdrawals, 
                max_withdrawals
            )
            max_withdrawals, count, remaining_capacity = res
            redistributed_count += count
    return max_withdrawals, redistributed_count


def redistribute_to_branch(
    branch: str, 
    product_index: int, 
    remaining_capacity: float, 
    branches: list,
    branch_data: dict, 
    analytics_data: dict, 
    all_withdrawals: dict,
    max_withdrawals: int
) -> tuple:
    """Attempt to redistribute surplus to a single branch."""
    return process_all_other_branches(
        branch, 
        product_index, 
        remaining_capacity, 
        branches,
        branch_data, 
        analytics_data, 
        all_withdrawals, 
        max_withdrawals
    )
