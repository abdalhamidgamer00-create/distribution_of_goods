"""Date extraction and validation logic."""
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

def extract_dates_from_header(header_text: str) -> tuple:
    """Extract start and end dates from header text."""
    date_pattern = r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})'
    dates = re.findall(date_pattern, header_text)
    return _parse_date_strings(dates) if len(dates) >= 2 else (None, None)


def calculate_days_between(start_date: datetime, end_date: datetime) -> int:
    """Calculate number of days between two dates (minimum 1)."""
    if not _validate_date_pair(start_date, end_date):
        return 0
    return max(1, (end_date - start_date).days)


def validate_date_range_months(start_date: datetime, end_date: datetime, min_months: int = 3) -> bool:
    """Validate that date range is at least min_months months."""
    if not _validate_date_pair(start_date, end_date):
        return False
    delta = relativedelta(end_date, start_date)
    return (delta.years * 12 + delta.months) >= min_months


def validate_csv_header(csv_path: str) -> tuple:
    """Validate CSV file header and extract date range."""
    try:
        return _extract_and_validate_dates(csv_path)
    except Exception as error:
        return False, None, None, f"Error reading file: {error}"


def _parse_date_strings(dates: list) -> tuple:
    """Parse date strings and return datetime objects."""
    try:
        start_date = datetime.strptime(dates[0], "%d/%m/%Y %H:%M")
        end_date = datetime.strptime(dates[1], "%d/%m/%Y %H:%M")
        return start_date, end_date
    except ValueError:
        return None, None


def _validate_date_pair(start_date: datetime, end_date: datetime) -> bool:
    """Validate that both dates exist and are in correct order."""
    if start_date is None or end_date is None:
        return False
    return end_date >= start_date


def _extract_and_validate_dates(csv_path: str) -> tuple:
    """Extract dates from header and validate."""
    with open(csv_path, 'r', encoding='utf-8-sig') as file_handle:
        first_line = file_handle.readline().strip()
    
    start_date, end_date = extract_dates_from_header(first_line)
    if start_date is None or end_date is None:
        return False, None, None, "Could not extract dates from header"
    
    is_valid = validate_date_range_months(start_date, end_date, 3)
    return is_valid, start_date, end_date, _build_date_message(start_date, end_date, is_valid)


def _build_date_message(start_date, end_date, is_valid: bool) -> str:
    """Build validation message for date range."""
    if is_valid:
        return f"Date range valid: {start_date.strftime('%d/%m/%Y %H:%M')} to {end_date.strftime('%d/%m/%Y %H:%M')} (>= 3 months)"
    
    delta = relativedelta(end_date, start_date)
    total_months = delta.years * 12 + delta.months
    return f"Date range invalid: {start_date.strftime('%d/%m/%Y %H:%M')} to {end_date.strftime('%d/%m/%Y %H:%M')} ({total_months} months, required: >= 3 months)"
