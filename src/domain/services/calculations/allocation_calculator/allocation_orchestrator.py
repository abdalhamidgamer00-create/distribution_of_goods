"""Main orchestration for allocation calculation."""

import pandas as pd
from src.domain.services.calculations.allocation_calculator import (
    matrices, scoring, proportions, redistribution
)


def process_single_product_allocation(
    product_index: int, allocation_matrices: dict, total_surplus: pd.Series, 
    total_needed: pd.Series, branches: list, branch_data: dict
) -> dict:
    """Process allocation for a single product."""
    if total_needed.loc[product_index] <= 0:
        return None
        
    total_scores = scoring.calculate_weighted_scores(
        allocation_matrices, product_index
    )
    allocated_dict = proportions.allocate_by_proportions(
        allocation_matrices, product_index, total_scores, 
        total_surplus.loc[product_index], total_needed.loc[product_index], 
        branches
    )
    return redistribution.redistribute_allocations(
        allocated_dict, 
        allocation_matrices['needed'].loc[product_index].to_dict(), 
        branch_data, product_index
    )


def collect_allocations(
    indices, allocation_matrices: dict, total_surplus, total_needed, 
    branches: list, branch_data: dict
) -> dict:
    """Collect allocations for all products needing allocation."""
    allocations = {}
    for product_index in indices:
        result = process_single_product_allocation(
            product_index, allocation_matrices, total_surplus, total_needed, 
            branches, branch_data
        )
        if result:
            allocations[product_index] = result
    return allocations


def calculate_proportional_allocations_vectorized(
    branch_data: dict, branches: list
) -> dict:
    """Vectorized proportional allocation across all products."""
    if not branch_data:
        return {}
    
    alloc_matrices, total_needed, total_surplus, needs_mask = \
        matrices.setup_allocation_data(branch_data, branches)
    
    return collect_allocations(
        total_needed[needs_mask].index, alloc_matrices, total_surplus, 
        total_needed, branches, branch_data
    )
