"""Branch ordering calculations"""

# Weights matching proportional allocation
BALANCE_WEIGHT = 0.60
NEEDED_WEIGHT = 0.30
AVG_SALES_WEIGHT = 0.10


def _calculate_priority_score(needed: float, balance: float, avg_sales: float) -> float:
    """Calculate weighted priority score for a branch."""
    inverse_balance_score = 1.0 / (balance + 0.1)  # +0.1 to avoid division by zero
    return (
        BALANCE_WEIGHT * inverse_balance_score +
        NEEDED_WEIGHT * needed +
        AVG_SALES_WEIGHT * avg_sales
    )


def get_needing_branches_order_for_product(product_index: int, branch_data: dict, branches: list) -> list:
    """Get order of branches that need products, sorted by weighted priority score."""
    needing_branches = []
    
    for branch in branches:
        needed = branch_data[branch].iloc[product_index]['needed_quantity']
        if needed > 0:
            avg_sales = branch_data[branch].iloc[product_index]['avg_sales']
            balance = branch_data[branch].iloc[product_index]['balance']
            score = _calculate_priority_score(needed, balance, avg_sales)
            needing_branches.append((branch, score))
    
    needing_branches.sort(key=lambda x: -x[1])
    return [b[0] for b in needing_branches]


def _calculate_single_branch_surplus(other_branch: str, product_index: int, branch_data: dict, 
                                      existing_withdrawals: dict) -> tuple:
    """Calculate available surplus for a single branch."""
    original_surplus = branch_data[other_branch].iloc[product_index]['surplus_quantity']
    already_withdrawn = existing_withdrawals.get((other_branch, product_index), 0.0)
    available_surplus = round(max(0, original_surplus - already_withdrawn), 2)
    
    if available_surplus > 0:
        balance = branch_data[other_branch].iloc[product_index]['balance']
        avg_sales = branch_data[other_branch].iloc[product_index]['avg_sales']
        return (other_branch, available_surplus, balance, avg_sales)
    return None


def _collect_branch_surpluses(product_index: int, branch: str, branch_data: dict, 
                               branches: list, existing_withdrawals: dict) -> list:
    """Collect surplus info for all branches except current."""
    branch_surplus = []
    for other_branch in branches:
        if other_branch != branch:
            result = _calculate_single_branch_surplus(other_branch, product_index, branch_data, existing_withdrawals)
            if result:
                branch_surplus.append(result)
    return branch_surplus


def get_surplus_branches_order_for_product(product_index: int, branch: str, branch_data: dict, 
                                           branches: list, existing_withdrawals: dict = None) -> list:
    """Get order of branches to search for surplus based on available surplus quantity."""
    if existing_withdrawals is None:
        existing_withdrawals = {}
    
    branch_surplus = _collect_branch_surpluses(product_index, branch, branch_data, branches, existing_withdrawals)
    branch_surplus.sort(key=lambda x: (-x[1], -x[2], x[3]))
    return [b[0] for b in branch_surplus]


