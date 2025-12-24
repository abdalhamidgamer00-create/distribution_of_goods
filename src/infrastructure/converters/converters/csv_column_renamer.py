"""CSV column renamer"""

import pandas as pd
from src.infrastructure.converters.mappers.column_mapper import get_column_mapping


def _read_csv_with_date_detection(csv_path: str) -> tuple:
    """Read CSV and detect date header."""
    with open(csv_path, 'r', encoding='utf-8-sig') as file:
        first_line = file.readline().strip()
    
    from src.domain.services.validation import extract_dates_from_header
    start_date, end_date = extract_dates_from_header(first_line)
    
    if start_date and end_date:
        dataframe = pd.read_csv(csv_path, skiprows=1, encoding='utf-8-sig')
        return dataframe, True, first_line
        
    dataframe = pd.read_csv(csv_path, encoding='utf-8-sig')
    return dataframe, False, first_line


def _write_renamed_csv(
    dataframe: pd.DataFrame, 
    path: str, 
    has_header: bool, 
    first_line: str
) -> None:
    """Write DataFrame with optional date header."""
    with open(path, 'w', encoding='utf-8-sig', newline='') as file:
        if has_header:
            file.write(first_line + '\n')
        dataframe.to_csv(file, index=False, lineterminator='\n')


def rename_csv_columns(csv_path: str, output_path: str) -> bool:
    """Rename CSV columns from Arabic to English."""
    try:
        result = _read_csv_with_date_detection(csv_path)
        dataframe, has_header, first_line = result
        
        dataframe.rename(columns=get_column_mapping(), inplace=True)
        _write_renamed_csv(dataframe, output_path, has_header, first_line)
        return True
    except Exception as error:
        raise ValueError(f"Error renaming columns: {error}")
