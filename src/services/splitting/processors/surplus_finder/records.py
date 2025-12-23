"""Withdrawal record creation helpers."""

import math


def create_empty_withdrawal_record(remaining_needed: float = 0.0) -> dict:
    """Create a standard empty withdrawal record."""
    return {
        'surplus_from_branch': 0.0,
        'available_branch': '',
        'surplus_remaining': 0.0,
        'remaining_needed': math.ceil(
            remaining_needed
        ) if remaining_needed > 0 else 0.0
    }


def finalize_withdrawals(
    withdrawals_for_row: list, remaining_needed: float
) -> tuple:
    """Finalize withdrawal results."""
    if not withdrawals_for_row:
        return [create_empty_withdrawal_record(remaining_needed)], {}
    
    withdrawals_for_row[-1]['remaining_needed'] = math.ceil(remaining_needed)
    return withdrawals_for_row, None  # None signals to use existing withdrawals
