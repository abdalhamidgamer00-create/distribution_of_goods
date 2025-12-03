"""CSV column renamer"""

import pandas as pd

from src.services.conversion.mappers.column_mapper import get_column_mapping


def rename_csv_columns(csv_path: str, output_path: str) -> bool:
    """
    Rename CSV columns from Arabic to English
    
    Args:
        csv_path: Input CSV file path
        output_path: Output CSV file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline().strip()
        
        from src.core.validation.data_validator import extract_dates_from_header
        start_date, end_date = extract_dates_from_header(first_line)
        
        if start_date and end_date:
            df = pd.read_csv(csv_path, skiprows=1, encoding='utf-8-sig')
            has_date_header = True
        else:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
            has_date_header = False
        
        column_mapping = get_column_mapping()
        df.rename(columns=column_mapping, inplace=True)
        
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            if has_date_header:
                f.write(first_line + '\n')
            df.to_csv(f, index=False, lineterminator='\n')
        
        return True
        
    except Exception as e:
        raise ValueError(f"Error renaming columns: {e}")

