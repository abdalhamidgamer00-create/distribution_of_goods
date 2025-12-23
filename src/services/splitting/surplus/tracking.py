"""Data tracking and state management for surplus redistribution."""

def get_branch_product_data(
    analytics_data: dict, branch: str, product_index: int
) -> tuple:
    """Get branch product data (balance, needed, avg_sales)."""
    df = analytics_data[branch][0]
    row = df.iloc[product_index]
    return (
        row['balance'], 
        row['needed_quantity'], 
        row['avg_sales']
    )


def calculate_transferred_amount(
    analytics_data: dict, branch: str, product_index: int
) -> float:
    """Calculate total amount already transferred to a branch for a product."""
    withdrawals_list = analytics_data[branch][1]
    if product_index >= len(withdrawals_list):
        return 0.0
    
    withdrawals = withdrawals_list[product_index]
    return sum(w.get('surplus_from_branch', 0.0) for w in withdrawals)


def _append_withdrawal(
    withdrawals_list: list, 
    product_idx: int, 
    amount: float, 
    other_branch: str, 
    available_surplus: float
) -> int:
    """Append withdrawal entry and return max withdrawals count."""
    if product_idx < len(withdrawals_list):
        withdrawals_list[product_idx].append({
            'surplus_from_branch': amount, 
            'available_branch': other_branch, 
            'surplus_remaining': available_surplus - amount, 
            'remaining_needed': 0.0
        })
        return len(withdrawals_list[product_idx])
    return 0


def record_redistribution(
    branch: str, 
    other_branch: str, 
    product_idx: int, 
    amount: float,
    available_surplus: float, 
    analytics_data: dict, 
    all_withdrawals: dict,
    max_with: int
) -> int:
    """Record a redistribution in the tracking structures."""
    key = (other_branch, product_idx)
    all_withdrawals[key] = all_withdrawals.get(key, 0.0) + amount
    
    withdrawals_list = analytics_data[branch][1]
    count = _append_withdrawal(
        withdrawals_list, product_idx, amount, other_branch, available_surplus
    )
    return max(max_with, count)
