"""Data tracking and state management for surplus redistribution."""

def get_branch_product_data(analytics_data: dict, branch: str, product_index: int) -> tuple:
    """Get branch product data (balance, needed, avg_sales)."""
    branch_dataframe = analytics_data[branch][0]
    return (branch_dataframe.iloc[product_index]['balance'], 
            branch_dataframe.iloc[product_index]['needed_quantity'], 
            branch_dataframe.iloc[product_index]['avg_sales'])


def calculate_transferred_amount(analytics_data: dict, branch: str, product_index: int) -> float:
    """Calculate total amount already transferred to a branch for a product."""
    withdrawals_list = analytics_data[branch][1]
    if product_index >= len(withdrawals_list):
        return 0.0
    
    return sum(withdrawal.get('surplus_from_branch', 0.0) for withdrawal in withdrawals_list[product_index])


def _append_withdrawal(withdrawals_list: list, product_index: int, transfer_amount: float, 
                        other_branch: str, available_surplus: float) -> int:
    """Append withdrawal entry and return max withdrawals count."""
    if product_index < len(withdrawals_list):
        withdrawals_list[product_index].append({
            'surplus_from_branch': transfer_amount, 
            'available_branch': other_branch, 
            'surplus_remaining': available_surplus - transfer_amount, 
            'remaining_needed': 0.0
        })
        return len(withdrawals_list[product_index])
    return 0


def record_redistribution(branch: str, other_branch: str, product_index: int, transfer_amount: float,
                           available_surplus: float, analytics_data: dict, all_withdrawals: dict,
                           max_withdrawals: int) -> int:
    """Record a redistribution in the tracking structures."""
    key = (other_branch, product_index)
    all_withdrawals[key] = all_withdrawals.get(key, 0.0) + transfer_amount
    
    count = _append_withdrawal(analytics_data[branch][1], product_index, transfer_amount, other_branch, available_surplus)
    return max(max_withdrawals, count)
