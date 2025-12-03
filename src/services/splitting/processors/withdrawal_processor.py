"""Withdrawal processing and column addition"""


def process_withdrawals(branches: list, analytics_data: dict, max_withdrawals: int, final_surplus_remaining_dict: dict) -> dict:
    """
    Process withdrawals and add numbered columns to branch dataframes
    
    Args:
        branches: List of branch names
        analytics_data: Dictionary mapping branch to (branch_df, withdrawals_list)
        max_withdrawals: Maximum number of withdrawal columns
        final_surplus_remaining_dict: Dictionary mapping branch to list of surplus_remaining values
        
    Returns:
        Dictionary mapping branch to processed branch_df
    """
    processed_data = {}
    
    for branch in branches:
        branch_df, withdrawals_list = analytics_data[branch]
        
        for num in range(1, max_withdrawals + 1):
            surplus_from_branch_col = []
            available_branch_col = []
            surplus_remaining_col = []
            remaining_needed_col = []
            
            for row_idx, withdrawals_for_row in enumerate(withdrawals_list):
                if num <= len(withdrawals_for_row):
                    w = withdrawals_for_row[num - 1]
                    surplus_from_branch_col.append(w['surplus_from_branch'])
                    available_branch_col.append(w['available_branch'])
                    if w['available_branch']:
                        source_branch = w['available_branch']
                        surplus_remaining_col.append(final_surplus_remaining_dict[source_branch][row_idx])
                    else:
                        surplus_remaining_col.append(w['surplus_remaining'])
                    remaining_needed_col.append(w['remaining_needed'])
                else:
                    surplus_from_branch_col.append(0.0)
                    available_branch_col.append('')
                    surplus_remaining_col.append(0.0)
                    remaining_needed_col.append(0.0)
            
            branch_df[f'surplus_from_branch_{num}'] = surplus_from_branch_col
            branch_df[f'available_branch_{num}'] = available_branch_col
            branch_df[f'surplus_remaining_{num}'] = surplus_remaining_col
            branch_df[f'remaining_needed_{num}'] = remaining_needed_col
        
        processed_data[branch] = branch_df
    
    return processed_data

