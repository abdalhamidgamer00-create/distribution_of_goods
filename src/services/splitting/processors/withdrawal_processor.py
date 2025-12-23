"""Withdrawal processing and column addition"""


# =============================================================================
# PUBLIC API
# =============================================================================

def process_withdrawals(
    branches: list, 
    analytics_data: dict, 
    max_withdrawals: int, 
    final_surplus_dict: dict
) -> dict:
    """Process withdrawals and add numbered columns to branch dataframes."""
    processed_data = {}
    
    for branch in branches:
        branch_df, withdrawals_list = analytics_data[branch]
        processed_data[branch] = _add_withdrawal_columns(
            branch_df, withdrawals_list, max_withdrawals, final_surplus_dict
        )
    
    return processed_data


# =============================================================================
# DATA EXTRACTION HELPERS
# =============================================================================

def _extract_withdrawal_data(
    withdrawal: dict, 
    row_index: int, 
    final_surplus_dict: dict
) -> tuple:
    """Extract data from a single withdrawal entry."""
    amount = withdrawal['surplus_from_branch']
    branch = withdrawal['available_branch']
    needed = withdrawal['remaining_needed']
    
    if branch:
        surplus_rem = final_surplus_dict[branch][row_index]
    else:
        surplus_rem = withdrawal['surplus_remaining']
        
    return amount, branch, surplus_rem, needed


def _get_empty_column_data() -> tuple:
    """Return empty column data tuple."""
    return 0.0, '', 0.0, 0.0


# =============================================================================
# COLUMN BUILDING HELPERS
# =============================================================================

def _collect_column_data(
    withdrawals_list: list, 
    col_num: int, 
    final_surplus_dict: dict
) -> list:
    """Collect column data for all rows."""
    result = []
    for row_idx, withdrawals_for_row in enumerate(withdrawals_list):
        if col_num <= len(withdrawals_for_row):
            withdrawal = withdrawals_for_row[col_num - 1]
            extracted = _extract_withdrawal_data(
                withdrawal, row_idx, final_surplus_dict
            )
            result.append(extracted)
        else:
            result.append(_get_empty_column_data())
    return result


def _build_single_column_set(
    withdrawals_list: list, 
    col_num: int, 
    final_surplus_dict: dict
) -> tuple:
    """Build column data for a single withdrawal number."""
    data_list = _collect_column_data(
        withdrawals_list, col_num, final_surplus_dict
    )
    return tuple(zip(*data_list))


def _add_withdrawal_columns(
    branch_df, 
    withdrawals_list: list, 
    max_with: int, 
    final_surplus_dict: dict
):
    """Add numbered withdrawal columns to branch DataFrame."""
    for num in range(1, max_with + 1):
        cols = _build_single_column_set(
            withdrawals_list, num, final_surplus_dict
        )
        branch_df[f'surplus_from_branch_{num}'] = cols[0]
        branch_df[f'available_branch_{num}'] = cols[1]
        branch_df[f'surplus_remaining_{num}'] = cols[2]
        branch_df[f'remaining_needed_{num}'] = cols[3]
    return branch_df
