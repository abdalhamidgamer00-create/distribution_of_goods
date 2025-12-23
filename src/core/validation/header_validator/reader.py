"""Header reading logic."""

from src.core.validation.dates import extract_dates_from_header

def read_header_line(csv_path: str) -> tuple:
    """Read and parse header line from CSV file."""
    with open(csv_path, 'r', encoding='utf-8-sig') as file_handle:
        first_line = file_handle.readline().strip()
        start_date, end_date = extract_dates_from_header(first_line)
        second_line = file_handle.readline().strip() if start_date and end_date else first_line
    return second_line
