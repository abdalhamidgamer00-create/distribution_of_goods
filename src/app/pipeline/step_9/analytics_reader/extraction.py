"""Withdrawal extraction logic."""

import pandas as pd

def build_withdrawal_pairs(dataframe: pd.DataFrame) -> list:
    """Build withdrawal column pairs."""
    surplus_from_columns = [column for column in dataframe.columns if column.startswith('surplus_from_branch_')]
    available_branch_columns = [column for column in dataframe.columns if column.startswith('available_branch_')]
    min_columns = min(len(surplus_from_columns), len(available_branch_columns))
    return list(zip(available_branch_columns[:min_columns], surplus_from_columns[:min_columns]))


def extract_withdrawal_amount(row, available_column: str, surplus_column: str, source_branch: str) -> float:
    """Extract withdrawal amount from a single column pair."""
    if pd.notna(row.get(available_column)) and str(row[available_column]).strip() == source_branch:
        if pd.notna(row.get(surplus_column)):
            try:
                return float(row[surplus_column])
            except (ValueError, TypeError):
                pass
    return 0.0


def process_withdrawal_row(row, source_branch: str, withdrawal_pairs: list) -> dict:
    """Process a single row and extract withdrawals from source branch."""
    product_code = row.get('code')
    if pd.isna(product_code):
        return {}
    
    product_code = str(product_code)
    total = sum(extract_withdrawal_amount(row, available, surplus, source_branch) for available, surplus in withdrawal_pairs)
    return {product_code: total} if total > 0 else {}


def extract_withdrawals_from_branch(dataframe: pd.DataFrame, source_branch: str) -> dict:
    """Extract all withdrawals made FROM a specific branch."""
    withdrawal_pairs = build_withdrawal_pairs(dataframe)
    
    all_withdrawals = {}
    for _, row in dataframe.iterrows():
        row_withdrawals = process_withdrawal_row(row, source_branch, withdrawal_pairs)
        for code, amount in row_withdrawals.items():
            all_withdrawals[code] = all_withdrawals.get(code, 0.0) + amount
    
    return all_withdrawals
