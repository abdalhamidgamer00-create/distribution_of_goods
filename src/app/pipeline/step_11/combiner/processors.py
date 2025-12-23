"""Processor helpers for DataFrames."""
import pandas as pd
from typing import Dict

def filter_self_transfers(combined: pd.DataFrame, branch: str) -> pd.DataFrame:
    """Filter out self-transfers from combined data."""
    if 'target_branch' in combined.columns:
        return combined[combined['target_branch'] != branch]
    return combined


def add_balance_columns(
    df: pd.DataFrame, 
    sender_balances: Dict[str, float], 
    receiver_balances: Dict[str, float]
) -> pd.DataFrame:
    """Add sender and receiver balance columns to DataFrame."""
    df['sender_balance'] = df['code'].apply(lambda x: sender_balances.get(str(x), 0))
    df['receiver_balance'] = df['code'].apply(lambda x: receiver_balances.get(str(x), 0))
    return df


def normalize_surplus_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize surplus column names to standard quantity columns."""
    surplus_cols = ['surplus_remaining', 'remaining_surplus', 'surplus_quantity']
    for col in surplus_cols:
        if col in df.columns:
            df['quantity'] = df[col]
            df['quantity_to_transfer'] = df[col]
            break
    return df


def extract_target_branch(filename: str) -> str:
    """Extract target branch name from transfer filename."""
    name = filename.replace('.csv', '')  # Remove .csv extension first
    # Pattern: ..._from_X_to_Y or ..._to_Y
    if '_to_' in name:
        parts = name.split('_to_')
        if len(parts) > 1:
            return parts[-1].split('_')[0]  # Get first word after _to_
    return 'unknown'
