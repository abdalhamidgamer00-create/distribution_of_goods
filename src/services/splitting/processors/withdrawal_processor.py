"""Withdrawal processing and column addition"""


def _extract_withdrawal_data(withdrawal: dict, row_idx: int, final_surplus_remaining_dict: dict) -> tuple:
    """Extract data from a single withdrawal entry."""
    surplus_from_branch = withdrawal['surplus_from_branch']
    available_branch = withdrawal['available_branch']
    remaining_needed = withdrawal['remaining_needed']
    
    if available_branch:
        surplus_remaining = final_surplus_remaining_dict[available_branch][row_idx]
    else:
        surplus_remaining = withdrawal['surplus_remaining']
    
    return surplus_from_branch, available_branch, surplus_remaining, remaining_needed


def _add_withdrawal_columns(branch_df, withdrawals_list: list, max_withdrawals: int, final_surplus_remaining_dict: dict):
    """Add numbered withdrawal columns to branch DataFrame."""
    for num in range(1, max_withdrawals + 1):
        surplus_from_branch_col = []
        available_branch_col = []
        surplus_remaining_col = []
        remaining_needed_col = []
        
        for row_idx, withdrawals_for_row in enumerate(withdrawals_list):
            if num <= len(withdrawals_for_row):
                data = _extract_withdrawal_data(withdrawals_for_row[num - 1], row_idx, final_surplus_remaining_dict)
                surplus_from_branch_col.append(data[0])
                available_branch_col.append(data[1])
                surplus_remaining_col.append(data[2])
                remaining_needed_col.append(data[3])
            else:
                surplus_from_branch_col.append(0.0)
                available_branch_col.append('')
                surplus_remaining_col.append(0.0)
                remaining_needed_col.append(0.0)
        
        branch_df[f'surplus_from_branch_{num}'] = surplus_from_branch_col
        branch_df[f'available_branch_{num}'] = available_branch_col
        branch_df[f'surplus_remaining_{num}'] = surplus_remaining_col
        branch_df[f'remaining_needed_{num}'] = remaining_needed_col
    
    return branch_df


def process_withdrawals(branches: list, analytics_data: dict, max_withdrawals: int, final_surplus_remaining_dict: dict) -> dict:
    """Process withdrawals and add numbered columns to branch dataframes."""
    processed_data = {}
    
    for branch in branches:
        branch_df, withdrawals_list = analytics_data[branch]
        processed_data[branch] = _add_withdrawal_columns(branch_df, withdrawals_list, max_withdrawals, final_surplus_remaining_dict)
    
    return processed_data


