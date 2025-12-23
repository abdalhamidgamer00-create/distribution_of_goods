"""CSV column renamer"""

import pandas as pd

from src.services.conversion.mappers.column_mapper import get_column_mapping


def _read_csv_with_date_detection(csv_path: str) -> tuple:
    """Read CSV and detect date header."""
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        first_line = f.readline().strip()
    
    from src.core.validation import extract_dates_from_header
    start_date, end_date = extract_dates_from_header(first_line)
    
    if start_date and end_date:
        return pd.read_csv(csv_path, skiprows=1, encoding='utf-8-sig'), True, first_line
    return pd.read_csv(csv_path, encoding='utf-8-sig'), False, first_line


def _write_renamed_csv(df: pd.DataFrame, output_path: str, has_date_header: bool, first_line: str) -> None:
    """Write DataFrame with optional date header."""
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        if has_date_header:
            f.write(first_line + '\n')
        df.to_csv(f, index=False, lineterminator='\n')


def rename_csv_columns(csv_path: str, output_path: str) -> bool:
    """Rename CSV columns from Arabic to English."""
    try:
        df, has_date_header, first_line = _read_csv_with_date_detection(csv_path)
        df.rename(columns=get_column_mapping(), inplace=True)
        _write_renamed_csv(df, output_path, has_date_header, first_line)
        return True
    except Exception as e:
        raise ValueError(f"Error renaming columns: {e}")

