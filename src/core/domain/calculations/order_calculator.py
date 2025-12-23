"""Branch ordering calculations"""


# =============================================================================
# CONSTANTS
# =============================================================================

BALANCE_WEIGHT = 0.60
NEEDED_WEIGHT = 0.30
AVG_SALES_WEIGHT = 0.10


# =============================================================================
# PUBLIC API
# =============================================================================

def get_needing_branches_order_for_product(
    product_index: int, branch_data: dict, branches: list
) -> list:
    """Get order of branches that need products by weighted priority score."""
    needing_branches = _collect_needing_branches(
        product_index, branch_data, branches
    )
    needing_branches.sort(key=lambda item: -item[1])
    return [branch[0] for branch in needing_branches]


def get_surplus_branches_order_for_product(
    product_index: int, branch: str, branch_data: dict, 
    branches: list, existing_withdrawals: dict = None
) -> list:
    """Get order of branches to search for surplus."""
    if existing_withdrawals is None:
        existing_withdrawals = {}
    
    branch_surplus = _collect_branch_surpluses(
        product_index, branch, branch_data, branches, existing_withdrawals
    )
    branch_surplus.sort(key=lambda item: (-item[1], -item[2], item[3]))
    return [branch_tuple[0] for branch_tuple in branch_surplus]


# =============================================================================
# PRIORITY SCORE HELPERS
# =============================================================================

def _calculate_priority_score(
    needed: float, balance: float, avg_sales: float
) -> float:
    """Calculate weighted priority score for a branch."""
    inverse_balance_score = 1.0 / (balance + 0.1)  # Avoid division by zero
    return (
        BALANCE_WEIGHT * inverse_balance_score +
        NEEDED_WEIGHT * needed +
        AVG_SALES_WEIGHT * avg_sales
    )


# =============================================================================
# NEEDING BRANCHES HELPERS
# =============================================================================

def _collect_needing_branches(
    product_index: int, branch_data: dict, branches: list
) -> list:
    """Collect branches that need products with their scores."""
    needing_branches = []
    for branch in branches:
        row = branch_data[branch].iloc[product_index]
        needed = row['needed_quantity']
        if needed > 0:
            avg_sales = row['avg_sales']
            balance = row['balance']
            score = _calculate_priority_score(needed, balance, avg_sales)
            needing_branches.append((branch, score))
    return needing_branches


# =============================================================================
# SURPLUS BRANCHES HELPERS
# =============================================================================

def _calculate_single_branch_surplus(
    other_branch: str, product_index: int, branch_data: dict, 
    existing_withdrawals: dict
) -> tuple:
    """Calculate available surplus for a single branch."""
    row = branch_data[other_branch].iloc[product_index]
    original_surplus = row['surplus_quantity']
    already_withdrawn = existing_withdrawals.get(
        (other_branch, product_index), 0.0
    )
    available_surplus = round(max(0, original_surplus - already_withdrawn), 2)
    if available_surplus > 0:
        return (
            other_branch, available_surplus, row['balance'], row['avg_sales']
        )
    return None


def _collect_branch_surpluses(
    product_index: int, branch: str, branch_data: dict, 
    branches: list, existing_withdrawals: dict
) -> list:
    """Collect surplus info for all branches except current."""
    branch_surplus = []
    for other_branch in branches:
        if other_branch != branch:
            result = _calculate_single_branch_surplus(
                other_branch, product_index, branch_data, existing_withdrawals
            )
            if result:
                branch_surplus.append(result)
    return branch_surplus
