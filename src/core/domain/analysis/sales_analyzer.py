"""Sales data analyzer"""

import pandas as pd

from src.core.validation.data_validator import extract_dates_from_header


def analyze_csv_data(csv_path: str) -> dict:
    """
    Analyze CSV data and calculate statistics
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        Dictionary with analysis results
    """
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline().strip()
        
        date_range = None
        start_date, end_date = extract_dates_from_header(first_line)
        if start_date and end_date:
            date_range = {
                'start': start_date.strftime('%d/%m/%Y %H:%M'),
                'end': end_date.strftime('%d/%m/%Y %H:%M')
            }
            df = pd.read_csv(csv_path, skiprows=1, encoding='utf-8-sig')
        else:
            df = pd.read_csv(csv_path, encoding='utf-8-sig')
        
        total_rows = len(df)
        total_columns = len(df.columns)
        total_cells = total_rows * total_columns
        
        empty_cells = df.isna().sum().sum()
        empty_cells_percentage = (empty_cells / total_cells * 100) if total_cells > 0 else 0
        
        return {
            'date_range': date_range,
            'total_rows': total_rows,
            'total_columns': total_columns,
            'total_cells': total_cells,
            'empty_cells': int(empty_cells),
            'empty_cells_percentage': round(empty_cells_percentage, 2),
            'filled_cells': int(total_cells - empty_cells)
        }
        
    except Exception as e:
        raise ValueError(f"Error analyzing CSV: {e}")

