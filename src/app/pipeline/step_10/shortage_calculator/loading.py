"""Data loading logic for shortage calculation."""

import os
import pandas as pd
from src.shared.utils.file_handler import get_latest_file
from src.core.validation import extract_dates_from_header
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def load_analytics_dataframe(
    analytics_path: str, 
    has_date_header: bool
) -> pd.DataFrame:
    """Load analytics DataFrame with optional header skip."""
    skiprows = 1 if has_date_header else 0
    return pd.read_csv(analytics_path, skiprows=skiprows, encoding='utf-8-sig')


def read_analytics_file(analytics_path: str) -> tuple:
    """Read an analytics file and return its data."""
    try:
        with open(analytics_path, 'r', encoding='utf-8-sig') as file_handle:
            first_line = file_handle.readline().strip()
        start_date, end_date = extract_dates_from_header(first_line)
        has_date_header = bool(start_date and end_date)
        return (
            load_analytics_dataframe(analytics_path, has_date_header), 
            has_date_header, 
            first_line
        )
    except Exception as error:
        logger.error(
            "Error reading analytics file %s: %s", analytics_path, error
        )
        return None, False, ''


def load_and_validate_branch_analytics(
    analytics_dir: str, 
    branch: str
) -> tuple:
    """Load and validate analytics file for a branch."""
    branch_dir = os.path.join(analytics_dir, branch)
    latest_file = get_latest_file(branch_dir, '.csv')
    
    if not latest_file:
        logger.warning("No analytics file found for branch: %s", branch)
        return None, False, ''
    
    analytics_path = os.path.join(branch_dir, latest_file)
    return read_analytics_file(analytics_path)
