"""Sales data analyzer"""

import pandas as pd
from src.domain.services.validation import extract_dates_from_header


# =============================================================================
# PUBLIC API
# =============================================================================

def analyze_csv_data(csv_path: str) -> dict:
    """Analyze CSV data and calculate statistics."""
    try:
        dataframe, date_range = _read_csv_with_header(csv_path)
        stats = _calculate_cell_stats(dataframe)
        stats['date_range'] = date_range
        return stats
    except Exception as error:
        raise ValueError(f"Error analyzing CSV: {error}")


# =============================================================================
# FILE READING HELPERS
# =============================================================================

def _read_csv_with_header(csv_path: str) -> tuple:
    """Read CSV and detect date header."""
    with open(csv_path, 'r', encoding='utf-8-sig') as file_handle:
        first_line = file_handle.readline().strip()
    
    start_date, end_date = extract_dates_from_header(first_line)
    date_range = _build_date_range(start_date, end_date)
    
    skip = 1 if date_range else 0
    df = pd.read_csv(csv_path, skiprows=skip, encoding='utf-8-sig')
    return df, date_range


# =============================================================================
# DATE HELPERS
# =============================================================================

def _build_date_range(start_date, end_date) -> dict:
    """Build date range dictionary from dates."""
    if start_date and end_date:
        return {
            'start': start_date.strftime('%d/%m/%Y %H:%M'),
            'end': end_date.strftime('%d/%m/%Y %H:%M')
        }
    return None


# =============================================================================
# STATISTICS CALCULATION HELPERS
# =============================================================================

def _calculate_empty_percentage(empty_cells: int, total_cells: int) -> float:
    """Calculate empty cells percentage."""
    if total_cells == 0:
        return 0.0
    return round((empty_cells / total_cells * 100), 2)


def _calculate_cell_stats(dataframe) -> dict:
    """Calculate cell statistics from DataFrame."""
    rows, cols = len(dataframe), len(dataframe.columns)
    total_cells = rows * cols
    empty_cells = int(dataframe.isna().sum().sum())
    
    pct = _calculate_empty_percentage(empty_cells, total_cells)
    
    return {
        'total_rows': rows, 
        'total_columns': cols, 
        'total_cells': total_cells,
        'empty_cells': empty_cells, 
        'empty_cells_percentage': pct,
        'filled_cells': total_cells - empty_cells
    }
