"""Redistribution helpers."""


def get_sorted_zero_branches(
    branches_with_zero: list, branch_data: dict, product_index: int
) -> list:
    """Sort zero-allocation branches by avg_sales (desc) then balance (asc)."""
    scored = [(
        branch, 
        branch_data[branch].iloc[product_index]['avg_sales'], 
        branch_data[branch].iloc[product_index]['balance']
    ) for branch in branches_with_zero]
    
    scored.sort(key=lambda item: (-item[1], item[2]))
    return [item[0] for item in scored]


def perform_redistribution(
    allocated_dict: dict, branches_with_more: list, branches_with_zero: list
) -> dict:
    """Redistribute from branches with >1 to branches with 0."""
    for donor_branch in branches_with_more:
        if not branches_with_zero:
            break
        allocated_dict[donor_branch] -= 1
        recipient = branches_with_zero.pop(0)
        allocated_dict[recipient] = 1
    return allocated_dict


def redistribute_allocations(
    allocated_dict: dict, needed_dict: dict, branch_data: dict, 
    product_index: int
) -> dict:
    """Redistribute from branches with >1 to branches with 0."""
    branches_with_more = [
        branch for branch, amount in allocated_dict.items() 
        if amount > 1 and needed_dict.get(branch, 0) > 0
    ]
    branches_with_zero = [
        branch for branch, amount in allocated_dict.items() 
        if amount == 0 and needed_dict.get(branch, 0) > 0
    ]
    if not branches_with_zero:
        return allocated_dict
    
    sorted_zeros = get_sorted_zero_branches(
        branches_with_zero, branch_data, product_index
    )
    return perform_redistribution(
        allocated_dict, branches_with_more, sorted_zeros
    )
