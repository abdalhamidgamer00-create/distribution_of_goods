"""DataFrame builder logic for shortage calculation."""

import pandas as pd
from src.core.domain.branches.config import get_search_order


def get_shortage_columns() -> list:
    """Get ordered column list for shortage DataFrame."""
    ordered_branches = get_search_order()
    return (
        ['code', 'product_name', 'shortage_quantity', 'total_sales'] + 
        [f'balance_{branch}' for branch in ordered_branches]
    )


def build_shortage_row(code: str, totals: dict, branches: list) -> dict:
    """Build a single shortage row."""
    shortage_quantity = int(totals['total_needed'] - totals['total_surplus'])
    row_data = {
        'code': code, 
        'product_name': totals['product_name'], 
        'shortage_quantity': shortage_quantity, 
        'total_sales': int(totals['total_sales'])
    }
    for branch in branches:
        row_data[f'balance_{branch}'] = totals['branch_balances'].get(branch, 0)
    return row_data


def build_shortage_dataframe(
    product_totals: dict, 
    branches: list
) -> pd.DataFrame:
    """Build DataFrame from products with shortage (needed > surplus)."""
    shortage_data = [
        build_shortage_row(code, totals, branches) 
        for code, totals in product_totals.items() 
        if totals['total_needed'] > totals['total_surplus']
    ]
    columns = get_shortage_columns()
    if not shortage_data:
        return pd.DataFrame(columns=columns)
    
    return pd.DataFrame(shortage_data).sort_values(
        'shortage_quantity', ascending=False
    )[columns]
