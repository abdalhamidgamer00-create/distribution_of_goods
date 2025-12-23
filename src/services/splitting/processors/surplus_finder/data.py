"""Product data retrieval helpers."""


def get_product_data(branch_data: dict, branch: str, product_index: int) -> tuple:
    """Get needed and balance for a product."""
    branch_dataframe = branch_data[branch]
    return (
        branch_dataframe.iloc[product_index]['needed_quantity'], 
        branch_dataframe.iloc[product_index]['balance']
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
