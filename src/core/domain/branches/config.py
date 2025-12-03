"""Branch configuration settings"""


def get_branches() -> list:
    """
    Get list of branch names
    
    Returns:
        List of branch names
    """
    return ['asherin', 'wardani', 'akba', 'shahid', 'nujum', 'admin']


def get_search_order() -> list:
    """
    Get branch search order for finding surplus
    
    Returns:
        List of branch names in search order
    """
    return ['admin', 'nujum', 'akba', 'shahid', 'asherin', 'wardani']


def get_base_columns() -> list:
    """
    Get base columns that should be in all branch files
    
    Returns:
        List of base column names
    """
    return ['code', 'product_name', 'selling_price', 'company', 'unit', 
            'total_sales', 'total_product_balance']


def get_analytics_columns(max_withdrawals: int = 5) -> list:
    """
    Get analytics columns for separate analytics files
    
    Args:
        max_withdrawals: Maximum number of withdrawal columns to include
        
    Returns:
        List of analytics column names
    """
    base_columns = ['code', 'product_name', 'sales', 'avg_sales', 'balance', 
                    'monthly_quantity', 'surplus_quantity', 'needed_quantity']
    
    withdrawal_columns = []
    for num in range(1, max_withdrawals + 1):
        withdrawal_columns.extend([
            f'surplus_from_branch_{num}',
            f'available_branch_{num}',
            f'surplus_remaining_{num}',
            f'remaining_needed_{num}'
        ])
    
    return base_columns + withdrawal_columns

