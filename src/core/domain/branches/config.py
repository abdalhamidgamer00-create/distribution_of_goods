"""Branch configuration settings"""


# =============================================================================
# PUBLIC API - BRANCH LISTS
# =============================================================================

def get_branches() -> list:
    """Get list of branch names."""
    return ['asherin', 'wardani', 'akba', 'shahid', 'nujum', 'admin']


def get_search_order() -> list:
    """Get branch search order for finding surplus."""
    return ['admin', 'nujum', 'akba', 'shahid', 'asherin', 'wardani']


# =============================================================================
# PUBLIC API - COLUMN DEFINITIONS
# =============================================================================

def get_base_columns() -> list:
    """Get base columns that should be in all branch files."""
    return ['code', 'product_name', 'selling_price', 'company', 'unit', 
            'total_sales', 'total_product_balance']


def get_analytics_columns(max_withdrawals: int = 5) -> list:
    """Get analytics columns for separate analytics files."""
    base_columns = ['code', 'product_name', 'sales', 'avg_sales', 'balance', 
                    'monthly_quantity', 'surplus_quantity', 'needed_quantity']
    return base_columns + _build_withdrawal_columns(max_withdrawals)


# =============================================================================
# COLUMN BUILDING HELPERS
# =============================================================================

def _build_withdrawal_columns(max_withdrawals: int) -> list:
    """Build withdrawal column names for analytics files."""
    withdrawal_columns = []
    for column_number in range(1, max_withdrawals + 1):
        withdrawal_columns.extend([
            f'surplus_from_branch_{column_number}',
            f'available_branch_{column_number}',
            f'surplus_remaining_{column_number}',
            f'remaining_needed_{column_number}'
        ])
    return withdrawal_columns
