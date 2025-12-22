"""Proportional allocation calculations"""

import pandas as pd
import math

# Allocation weights
AVG_SALES_WEIGHT = 0.10  # 10% - نشاط الفرع
NEEDED_WEIGHT = 0.30     # 30% - الاحتياج
BALANCE_WEIGHT = 0.60    # 60% - أولوية قصوى للرصيد المنخفض


def _build_branch_matrices(branch_data: dict, branches: list) -> dict:
    """Build DataFrames for each metric from branch data."""
    return {
        'avg_sales': pd.DataFrame({b: branch_data[b]['avg_sales'].astype(float) for b in branches}),
        'balance': pd.DataFrame({b: branch_data[b]['balance'].astype(float) for b in branches}),
        'needed': pd.DataFrame({b: branch_data[b]['needed_quantity'].astype(float) for b in branches}),
        'surplus': pd.DataFrame({b: branch_data[b]['surplus_quantity'].astype(float) for b in branches}),
    }


def _normalize_scores(series: pd.Series) -> pd.Series:
    """Normalize series to 0-1 range."""
    min_val, max_val = series.min(), series.max()
    if max_val - min_val == 0:
        return pd.Series([1.0] * len(series), index=series.index)
    return (series - min_val) / (max_val - min_val)


def _calculate_weighted_scores(matrices: dict, product_index: int) -> pd.Series:
    """Calculate weighted priority scores for each branch."""
    avg_sales_scores = matrices['avg_sales'].loc[product_index].clip(lower=0)
    needed_scores = matrices['needed'].loc[product_index].clip(lower=0)
    inverse_balance_scores = 1.0 / (matrices['balance'].loc[product_index] + 0.1)
    
    return (
        AVG_SALES_WEIGHT * _normalize_scores(avg_sales_scores) +
        NEEDED_WEIGHT * _normalize_scores(needed_scores) +
        BALANCE_WEIGHT * _normalize_scores(inverse_balance_scores)
    )


def _calculate_proportions(matrices: dict, product_index: int, total_scores: pd.Series, 
                            total_needed_value: float, branches: list) -> pd.Series:
    """Calculate allocation proportions for each branch."""
    needed_row = matrices['needed'].loc[product_index]
    needing_mask = needed_row > 0
    total_scores_sum = total_scores[needing_mask].sum()
    if total_scores_sum <= 0:
        return needed_row.clip(lower=0) / total_needed_value
    proportions = pd.Series([0.0] * len(branches), index=branches)
    proportions[needing_mask] = total_scores[needing_mask] / total_scores_sum
    return proportions


def _allocate_by_proportions(matrices: dict, product_index: int, total_scores: pd.Series,
                             total_surplus_value: float, total_needed_value: float, branches: list) -> dict:
    """Allocate surplus based on weighted proportions."""
    proportions = _calculate_proportions(matrices, product_index, total_scores, total_needed_value, branches)
    allocated = (proportions * total_surplus_value).apply(lambda x: math.floor(x))
    return {branch: int(amount) for branch, amount in allocated.items()}


def _get_sorted_zero_branches(branches_with_zero: list, branch_data: dict, product_index: int) -> list:
    """Sort zero-allocation branches by avg_sales (desc) then balance (asc)."""
    scored = [(b, branch_data[b].iloc[product_index]['avg_sales'], branch_data[b].iloc[product_index]['balance']) 
              for b in branches_with_zero]
    scored.sort(key=lambda x: (-x[1], x[2]))
    return [b[0] for b in scored]


def _perform_redistribution(allocated_dict: dict, branches_with_more: list, branches_with_zero: list) -> dict:
    """Redistribute from branches with >1 to branches with 0."""
    for donor_branch in branches_with_more:
        if not branches_with_zero:
            break
        allocated_dict[donor_branch] -= 1
        recipient = branches_with_zero.pop(0)
        allocated_dict[recipient] = 1
    return allocated_dict


def _redistribute_allocations(allocated_dict: dict, needed_dict: dict, 
                              branch_data: dict, product_index: int) -> dict:
    """Redistribute from branches with >1 to branches with 0."""
    branches_with_more = [b for b, amt in allocated_dict.items() if amt > 1 and needed_dict.get(b, 0) > 0]
    branches_with_zero = [b for b, amt in allocated_dict.items() if amt == 0 and needed_dict.get(b, 0) > 0]
    if not branches_with_zero:
        return allocated_dict
    sorted_zeros = _get_sorted_zero_branches(branches_with_zero, branch_data, product_index)
    return _perform_redistribution(allocated_dict, branches_with_more, sorted_zeros)


def _process_single_product_allocation(idx: int, matrices: dict, total_surplus: pd.Series, 
                                        total_needed: pd.Series, branches: list, branch_data: dict) -> dict:
    """Process allocation for a single product."""
    if total_needed.loc[idx] <= 0:
        return None
    total_scores = _calculate_weighted_scores(matrices, idx)
    allocated_dict = _allocate_by_proportions(matrices, idx, total_scores, total_surplus.loc[idx], total_needed.loc[idx], branches)
    return _redistribute_allocations(allocated_dict, matrices['needed'].loc[idx].to_dict(), branch_data, idx)


def _setup_allocation_data(branch_data: dict, branches: list) -> tuple:
    """Setup matrices and calculate totals for allocation."""
    matrices = _build_branch_matrices(branch_data, branches)
    total_needed = matrices['needed'].clip(lower=0).sum(axis=1)
    total_surplus = matrices['surplus'].clip(lower=0).sum(axis=1)
    needs_mask = (total_needed > 0) & (total_surplus > 0) & (total_surplus < total_needed)
    return matrices, total_needed, total_surplus, needs_mask


def _collect_allocations(indices, matrices: dict, total_surplus, total_needed, branches: list, branch_data: dict) -> dict:
    """Collect allocations for all products needing allocation."""
    allocations = {}
    for idx in indices:
        result = _process_single_product_allocation(idx, matrices, total_surplus, total_needed, branches, branch_data)
        if result:
            allocations[idx] = result
    return allocations


def calculate_proportional_allocations_vectorized(branch_data: dict, branches: list) -> dict:
    """Vectorized proportional allocation across all products."""
    if not branch_data:
        return {}
    
    matrices, total_needed, total_surplus, needs_mask = _setup_allocation_data(branch_data, branches)
    return _collect_allocations(total_needed[needs_mask].index, matrices, total_surplus, total_needed, branches, branch_data)


