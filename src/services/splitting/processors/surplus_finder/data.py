"""Product data retrieval helpers."""


def get_product_data(
    branch_data: dict, branch: str, product_index: int
) -> tuple:
    """Get needed and balance for a product."""
    df = branch_data[branch]
    row = df.iloc[product_index]
    return (
        row['needed_quantity'], 
        row['balance']
    )


def get_allocated_amount(
    product_index: int, branch: str, proportional_allocation: dict
) -> float:
    """Extract allocated amount from proportional allocation dictionary."""
    if product_index not in proportional_allocation:
        return None
    if branch not in proportional_allocation[product_index]:
        return None
    return proportional_allocation[product_index][branch]
