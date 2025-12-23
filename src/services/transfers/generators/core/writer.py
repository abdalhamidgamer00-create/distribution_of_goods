"""Transfer file writing logic."""

import os
import pandas as pd


def write_transfer_csv(
    transfer_dataframe: pd.DataFrame, 
    transfer_path: str, 
    has_date_header: bool, 
    first_line: str
) -> None:
    """Write transfer DataFrame to CSV file."""
    with open(
        transfer_path, 'w', encoding='utf-8-sig', newline=''
    ) as file_handle:
        if has_date_header:
            file_handle.write(first_line + '\n')
        transfer_dataframe.to_csv(
            file_handle, index=False, lineterminator='\n'
        )


def save_transfer_file(
    transfer_dataframe: pd.DataFrame, 
    transfers_dir: str, 
    source_branch: str,
    target_branch: str, 
    base_name: str, 
    has_date_header: bool, 
    first_line: str
) -> str:
    """Save transfer DataFrame to CSV file."""
    transfer_dir = os.path.join(
        transfers_dir, f"transfers_from_{source_branch}_to_other_branches"
    )
    os.makedirs(transfer_dir, exist_ok=True)
    
    transfer_file = f"{base_name}_from_{source_branch}_to_{target_branch}.csv"
    transfer_path = os.path.join(transfer_dir, transfer_file)
    
    write_transfer_csv(
        transfer_dataframe, transfer_path, has_date_header, first_line
    )
    return transfer_path
