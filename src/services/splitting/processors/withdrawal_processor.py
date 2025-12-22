"""Withdrawal processing and column addition"""


# =============================================================================
# PUBLIC API
# =============================================================================

def process_withdrawals(branches: list, analytics_data: dict, max_withdrawals: int, final_surplus_remaining_dict: dict) -> dict:
    """Process withdrawals and add numbered columns to branch dataframes."""
    processed_data = {}
    
    for branch in branches:
        branch_dataframe, withdrawals_list = analytics_data[branch]
        processed_data[branch] = _add_withdrawal_columns(branch_dataframe, withdrawals_list, max_withdrawals, final_surplus_remaining_dict)
    
    return processed_data


# =============================================================================
# DATA EXTRACTION HELPERS
# =============================================================================

def _extract_withdrawal_data(withdrawal: dict, row_index: int, final_surplus_remaining_dict: dict) -> tuple:
    """Extract data from a single withdrawal entry."""
    surplus_from_branch = withdrawal['surplus_from_branch']
    available_branch = withdrawal['available_branch']
    remaining_needed = withdrawal['remaining_needed']
    surplus_remaining = final_surplus_remaining_dict[available_branch][row_index] if available_branch else withdrawal['surplus_remaining']
    return surplus_from_branch, available_branch, surplus_remaining, remaining_needed


def _get_empty_column_data() -> tuple:
    """Return empty column data tuple."""
    return 0.0, '', 0.0, 0.0


# =============================================================================
# COLUMN BUILDING HELPERS
# =============================================================================

def _collect_column_data(withdrawals_list: list, column_number: int, final_surplus_remaining_dict: dict) -> list:
    """Collect column data for all rows."""
    result = []
    for row_index, withdrawals_for_row in enumerate(withdrawals_list):
        if column_number <= len(withdrawals_for_row):
            result.append(_extract_withdrawal_data(withdrawals_for_row[column_number - 1], row_index, final_surplus_remaining_dict))
        else:
            result.append(_get_empty_column_data())
    return result


def _build_single_column_set(withdrawals_list: list, column_number: int, final_surplus_remaining_dict: dict) -> tuple:
    """Build column data for a single withdrawal number."""
    data_list = _collect_column_data(withdrawals_list, column_number, final_surplus_remaining_dict)
    return tuple(zip(*data_list))


def _add_withdrawal_columns(branch_dataframe, withdrawals_list: list, max_withdrawals: int, final_surplus_remaining_dict: dict):
    """Add numbered withdrawal columns to branch DataFrame."""
    for column_number in range(1, max_withdrawals + 1):
        columns = _build_single_column_set(withdrawals_list, column_number, final_surplus_remaining_dict)
        branch_dataframe[f'surplus_from_branch_{column_number}'] = columns[0]
        branch_dataframe[f'available_branch_{column_number}'] = columns[1]
        branch_dataframe[f'surplus_remaining_{column_number}'] = columns[2]
        branch_dataframe[f'remaining_needed_{column_number}'] = columns[3]
    return branch_dataframe
