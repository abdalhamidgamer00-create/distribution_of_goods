"""Branch ordering calculations"""


def get_needing_branches_order_for_product(idx: int, branch_data: dict, branches: list) -> list:
    """
    Get order of branches that need products, sorted by avg_sales (descending) then balance (ascending)
    This determines which needing branch processes first for its needs
    
    Args:
        idx: Product index
        branch_data: Dictionary of all branch dataframes
        branches: List of all branch names
        
    Returns:
        List of branch names that need the product, sorted by: highest avg_sales, then lowest balance
    """
    needing_branches = []
    
    for branch in branches:
        needed = branch_data[branch].iloc[idx]['needed_quantity']
        if needed > 0:
            avg_sales = branch_data[branch].iloc[idx]['avg_sales']
            balance = branch_data[branch].iloc[idx]['balance']
            needing_branches.append((branch, avg_sales, balance))
    
    needing_branches.sort(key=lambda x: (-x[1], x[2]))
    
    return [b[0] for b in needing_branches]


def get_surplus_branches_order_for_product(idx: int, branch: str, branch_data: dict, branches: list, existing_withdrawals: dict = None) -> list:
    """
    Get order of branches to search for surplus based on available surplus quantity
    Branches with more surplus are searched first
    
    Args:
        idx: Product index
        branch: Current branch name (excluded from search)
        branch_data: Dictionary of all branch dataframes
        branches: List of all branch names
        existing_withdrawals: Dictionary of withdrawals already made (branch, idx) -> amount
        
    Returns:
        List of branch names sorted by available surplus quantity (descending)
    """
    if existing_withdrawals is None:
        existing_withdrawals = {}
    
    branch_surplus = []
    
    for other_branch in branches:
        if other_branch != branch:
            original_surplus = branch_data[other_branch].iloc[idx]['surplus_quantity']
            already_withdrawn = existing_withdrawals.get((other_branch, idx), 0.0)
            available_surplus = round(max(0, original_surplus - already_withdrawn), 2)
            
            if available_surplus > 0:
                branch_surplus.append((other_branch, available_surplus))
    
    branch_surplus.sort(key=lambda x: -x[1])
    
    return [b[0] for b in branch_surplus]

