"""Branch ordering calculations"""


def get_needing_branches_order_for_product(product_index: int, branch_data: dict, branches: list) -> list:
    """
    Get order of branches that need products, sorted by weighted score.
    Uses same weights as proportional allocation for consistency:
    - balance: 60% (lower balance = higher priority)
    - needed: 30% (higher need = higher priority)  
    - avg_sales: 10% (higher sales = higher priority)
    
    Args:
        product_index: Product index to check
        branch_data: Dictionary of all branch dataframes
        branches: List of all branch names
        
    Returns:
        List of branch names that need the product, sorted by priority score (descending)
    """
    # Weights matching proportional allocation
    BALANCE_WEIGHT = 0.60
    NEEDED_WEIGHT = 0.30
    AVG_SALES_WEIGHT = 0.10
    
    needing_branches = []
    
    for branch in branches:
        needed = branch_data[branch].iloc[product_index]['needed_quantity']
        if needed > 0:
            avg_sales = branch_data[branch].iloc[product_index]['avg_sales']
            balance = branch_data[branch].iloc[product_index]['balance']
            
            # Calculate weighted score
            # Higher score = higher priority
            inverse_balance_score = 1.0 / (balance + 0.1)  # +0.1 to avoid division by zero
            
            # Weighted score (no normalization needed for ordering)
            score = (
                BALANCE_WEIGHT * inverse_balance_score +
                NEEDED_WEIGHT * needed +
                AVG_SALES_WEIGHT * avg_sales
            )
            
            needing_branches.append((branch, score, avg_sales, balance))
    
    # Sort by score (descending) - higher score = higher priority
    needing_branches.sort(key=lambda x: -x[1])
    
    return [b[0] for b in needing_branches]


def get_surplus_branches_order_for_product(product_index: int, branch: str, branch_data: dict, branches: list, existing_withdrawals: dict = None) -> list:
    """
    Get order of branches to search for surplus based on available surplus quantity
    
    Sorting priority:
    1. Higher available surplus (descending)
    2. Higher balance (descending) - richer branches give first
    3. Lower avg_sales (ascending) - less active branches give first
    
    Args:
        product_index: Product index to check
        branch: Current branch name (excluded from search)
        branch_data: Dictionary of all branch dataframes
        branches: List of all branch names
        existing_withdrawals: Dictionary of withdrawals already made (branch, product_index) -> amount
        
    Returns:
        List of branch names sorted by priority
    """
    if existing_withdrawals is None:
        existing_withdrawals = {}
    
    branch_surplus = []
    
    for other_branch in branches:
        if other_branch != branch:
            original_surplus = branch_data[other_branch].iloc[product_index]['surplus_quantity']
            already_withdrawn = existing_withdrawals.get((other_branch, product_index), 0.0)
            available_surplus = round(max(0, original_surplus - already_withdrawn), 2)
            
            if available_surplus > 0:
                balance = branch_data[other_branch].iloc[product_index]['balance']
                avg_sales = branch_data[other_branch].iloc[product_index]['avg_sales']
                branch_surplus.append((other_branch, available_surplus, balance, avg_sales))
    
    # Sort by: surplus (desc), balance (desc), avg_sales (asc)
    branch_surplus.sort(key=lambda x: (-x[1], -x[2], x[3]))
    
    return [b[0] for b in branch_surplus]


