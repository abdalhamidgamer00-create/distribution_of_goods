"""Surplus availability checks."""
from src.services.splitting.processors.surplus_helpers import (
    calculate_available_surplus
)

def check_surplus_availability(
    branch_data: dict, 
    other_branch: str, 
    product_index: int, 
    all_withdrawals: dict, 
    remaining_capacity: float
) -> float:
    """Check availability and return transfer amount or 0."""
    available = calculate_available_surplus(
        branch_data, other_branch, product_index, all_withdrawals
    )
    if available <= 0:
        return 0.0
    return min(available, remaining_capacity)


def should_skip_branch(
    other_branch: str, branch: str, remaining_capacity: float
) -> bool:
    """Check if branch should be skipped (same branch or no capacity)."""
    return other_branch == branch or remaining_capacity <= 0
