"""Analytics helper functions."""

def initialize_analytics_data(branches: list, branch_data: dict) -> dict:
    """Initialize analytics data structure for each branch."""
    analytics_data = {}
    for branch in branches:
        branch_df = branch_data[branch].copy()
        analytics_data[branch] = (branch_df, [])
    return analytics_data


def create_empty_withdrawal_record() -> dict:
    """Create an empty withdrawal record."""
    return {
        'surplus_from_branch': 0.0,
        'available_branch': '',
        'surplus_remaining': 0.0,
        'remaining_needed': 0.0
    }


def update_analytics_data(branch: str, product_index: int, withdrawals_list: list, 
                            analytics_data: dict, max_withdrawals: int) -> int:
    """Update analytics data with new withdrawals."""
    existing_withdrawals_list = analytics_data[branch][1]
    while len(existing_withdrawals_list) < product_index:
        existing_withdrawals_list.append([create_empty_withdrawal_record()])
    existing_withdrawals_list.append(withdrawals_list)
    return max(max_withdrawals, len(withdrawals_list))


def merge_withdrawals(withdrawals: dict, all_withdrawals: dict) -> None:
    """Merge new withdrawals into all_withdrawals."""
    for key, amount in withdrawals.items():
        all_withdrawals[key] = all_withdrawals.get(key, 0.0) + amount


def fill_empty_product_records(branches: list, analytics_data: dict, num_products: int) -> None:
    """Add empty records for products that weren't processed."""
    for branch in branches:
        branch_df = analytics_data[branch][0]
        existing_list = analytics_data[branch][1]
        
        for product_index in range(len(existing_list), num_products):
            if branch_df.iloc[product_index]['needed_quantity'] <= 0:
                existing_list.append([create_empty_withdrawal_record()])
