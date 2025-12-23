"""Proportion calculation logic."""

import pandas as pd
import math
from src.core.domain.calculations.allocation_calculator import scoring


def calculate_proportions(
    matrices: dict, product_index: int, total_scores: pd.Series, 
    total_needed_value: float, branches: list
) -> pd.Series:
    """Calculate allocation proportions for each branch."""
    needed_row = matrices['needed'].loc[product_index]
    needing_mask = needed_row > 0
    total_scores_sum = total_scores[needing_mask].sum()
    if total_scores_sum <= 0:
        return needed_row.clip(lower=0) / total_needed_value
    proportions = pd.Series([0.0] * len(branches), index=branches)
    proportions[needing_mask] = total_scores[needing_mask] / total_scores_sum
    return proportions


def allocate_by_proportions(
    matrices: dict, product_index: int, total_scores: pd.Series,
    total_surplus_value: float, total_needed_value: float, branches: list
) -> dict:
    """Allocate surplus based on weighted proportions."""
    proportions = calculate_proportions(
        matrices, product_index, total_scores, total_needed_value, branches
    )
    allocated = (proportions * total_surplus_value).apply(
        lambda value: math.floor(value)
    )
    return {branch: int(amount) for branch, amount in allocated.items()}
