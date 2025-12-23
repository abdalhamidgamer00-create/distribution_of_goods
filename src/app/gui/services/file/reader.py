"""File reading logic."""
import pandas as pd
from typing import Optional

def read_file_content(
    file_path: str, 
    max_rows: int = 100
) -> Optional[pd.DataFrame]:
    """Read file content as DataFrame."""
    try:
        if file_path.endswith('.csv'):
            return _read_csv_file(file_path, max_rows)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path, nrows=max_rows)
        return None
    except Exception:
        return None

def _read_csv_file(
    file_path: str, 
    max_rows: int
) -> Optional[pd.DataFrame]:
    """Read CSV file with date header detection."""
    from src.core.validation.data_validator import (
        extract_dates_from_header
    )
    
    with open(file_path, 'r', encoding='utf-8-sig') as file_handle:
        first_line = file_handle.readline().strip()
    
    start_date, end_date = extract_dates_from_header(first_line)
    
    skip_rows = 1 if (start_date and end_date) else 0
    return pd.read_csv(
        file_path, 
        skiprows=skip_rows, 
        encoding='utf-8-sig', 
        nrows=max_rows
    )
