"""Main aggregation logic for combiner."""
import pandas as pd
from typing import Optional
from .readers import read_transfer_files, read_surplus_as_admin_transfer
from .processors import filter_self_transfers

def combine_transfers_and_surplus(
    branch: str, 
    transfers_dir: str, 
    surplus_dir: str, 
    analytics_dir: str,
) -> Optional[pd.DataFrame]:
    """Combine transfers and remaining surplus for a branch."""
    all_data = []
    
    transfers_df = read_transfer_files(branch, transfers_dir, analytics_dir)
    if transfers_df is not None and not transfers_df.empty:
        all_data.append(transfers_df)
        
    surplus_df = read_surplus_as_admin_transfer(
        branch, surplus_dir, analytics_dir
    )
    if surplus_df is not None and not surplus_df.empty:
        all_data.append(surplus_df)
        
    if not all_data:
        return None
    
    combined = pd.concat(all_data, ignore_index=True)
    return filter_self_transfers(combined, branch)
