"""CSV parsing logic."""

import pandas as pd
from src.core.validation import extract_dates_from_header
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def parse_csv_with_date_header(analytics_path: str, first_line: str) -> tuple:
    """Parse CSV with optional date header detection."""
    start_date, end_date = extract_dates_from_header(first_line)
    has_date_header = bool(start_date and end_date)
    
    if has_date_header:
        dataframe = pd.read_csv(
            analytics_path, skiprows=1, encoding='utf-8-sig'
        )
    else:
        dataframe = pd.read_csv(analytics_path, encoding='utf-8-sig')
    
    return dataframe, has_date_header


def read_analytics_file(analytics_path: str) -> tuple:
    """Read an analytics file and return its data."""
    try:
        with open(analytics_path, 'r', encoding='utf-8-sig') as f_handle:
            first_line = f_handle.readline().strip()
        
        dataframe, has_date_header = parse_csv_with_date_header(
            analytics_path, first_line
        )
        return dataframe, has_date_header, first_line
    except Exception as error:
        logger.error(
            "Error reading analytics file %s: %s", analytics_path, error
        )
        return None, False, ''
