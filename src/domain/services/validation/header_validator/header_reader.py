"""Header reading logic."""

from src.domain.services.validation.dates import extract_dates_from_header

def read_header_line(csv_path: str) -> tuple:
    """Read and parse header line from CSV file."""
    with open(csv_path, 'r', encoding='utf-8-sig') as file_handle:
        first_line = file_handle.readline().strip()
        start, end = extract_dates_from_header(first_line)
        
        if start and end:
            return file_handle.readline().strip()
            
        return first_line
