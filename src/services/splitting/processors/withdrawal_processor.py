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


def _get_empty_column_data() -> tuple:
    """Return empty column data tuple."""
    return 0.0, '', 0.0, 0.0


def _collect_column_data(withdrawals_list: list, num: int, final_surplus_remaining_dict: dict) -> list:
    """Collect column data for all rows."""
    result = []
    for row_idx, withdrawals_for_row in enumerate(withdrawals_list):
        if num <= len(withdrawals_for_row):
            result.append(_extract_withdrawal_data(withdrawals_for_row[num - 1], row_idx, final_surplus_remaining_dict))
        else:
            result.append(_get_empty_column_data())
    return result


def _build_single_column_set(withdrawals_list: list, num: int, final_surplus_remaining_dict: dict) -> tuple:
    """Build column data for a single withdrawal number."""
    data_list = _collect_column_data(withdrawals_list, num, final_surplus_remaining_dict)
    return tuple(zip(*data_list))


def _add_withdrawal_columns(branch_df, withdrawals_list: list, max_withdrawals: int, final_surplus_remaining_dict: dict):
    """Add numbered withdrawal columns to branch DataFrame."""
    for num in range(1, max_withdrawals + 1):
        cols = _build_single_column_set(withdrawals_list, num, final_surplus_remaining_dict)
        branch_df[f'surplus_from_branch_{num}'] = cols[0]
        branch_df[f'available_branch_{num}'] = cols[1]
        branch_df[f'surplus_remaining_{num}'] = cols[2]
        branch_df[f'remaining_needed_{num}'] = cols[3]
    return branch_df


def process_withdrawals(branches: list, analytics_data: dict, max_withdrawals: int, final_surplus_remaining_dict: dict) -> dict:
    """Process withdrawals and add numbered columns to branch dataframes."""
    processed_data = {}
    
    for branch in branches:
        branch_df, withdrawals_list = analytics_data[branch]
        processed_data[branch] = _add_withdrawal_columns(branch_df, withdrawals_list, max_withdrawals, final_surplus_remaining_dict)
    
    return processed_data


