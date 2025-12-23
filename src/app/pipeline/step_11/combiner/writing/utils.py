"""Helper functions for writers."""
from datetime import datetime
import pandas as pd

def get_timestamp() -> str:
    """Get current timestamp for filenames."""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def prepare_and_sort(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare columns and sort DataFrame."""
    required_cols = [
        'code', 
        'product_name', 
        'quantity_to_transfer', 
        'target_branch', 
        'transfer_type', 
        'sender_balance', 
        'receiver_balance'
    ]
    optional_cols = ['unit', 'selling_price', 'company']
    
    final_cols = [c for c in required_cols if c in df.columns]
    final_cols.extend(c for c in optional_cols if c in df.columns)
    
    out = df[final_cols].copy()
    if 'product_name' in out.columns:
        return out.sort_values(
            'product_name', 
            ascending=True, 
            key=lambda x: x.str.lower()
        )
    return out
