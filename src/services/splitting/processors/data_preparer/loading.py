"""File reading helpers."""

import pandas as pd


def read_first_line(csv_path: str) -> str:
    """Read the first line from a CSV file."""
    with open(csv_path, 'r', encoding='utf-8-sig') as file_handle:
        return file_handle.readline().strip()


def read_csv_with_header(csv_path: str, header_contained_dates: bool) -> pd.DataFrame:
    """Read CSV file, skipping date header if present."""
    if header_contained_dates:
        dataframe = pd.read_csv(csv_path, skiprows=1, encoding='utf-8-sig')
    else:
        dataframe = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    if dataframe.empty:
        raise ValueError("CSV file contains no data")
    
    return dataframe
