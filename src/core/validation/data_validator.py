"""Data validation utilities"""

import re
from datetime import datetime
from dateutil.relativedelta import relativedelta


def extract_dates_from_header(header_text: str) -> tuple:
    """
    Extract start and end dates from header text
    
    Args:
        header_text: Header text containing date range
        
    Returns:
        Tuple of (start_date, end_date) as datetime objects, or (None, None) if not found
    """
    date_pattern = r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})'
    dates = re.findall(date_pattern, header_text)
    
    if len(dates) >= 2:
        try:
            start_date = datetime.strptime(dates[0], "%d/%m/%Y %H:%M")
            end_date = datetime.strptime(dates[1], "%d/%m/%Y %H:%M")
            return start_date, end_date
        except ValueError:
            return None, None
    
    return None, None


def validate_date_range_months(start_date: datetime, end_date: datetime, min_months: int = 3) -> bool:
    """
    Validate that date range is at least min_months months
    
    Args:
        start_date: Start date
        end_date: End date
        min_months: Minimum number of months (default: 3)
        
    Returns:
        True if date range >= min_months, False otherwise
    """
    if start_date is None or end_date is None:
        return False
    
    if end_date < start_date:
        return False
    
    delta = relativedelta(end_date, start_date)
    total_months = delta.years * 12 + delta.months
    
    return total_months >= min_months


def validate_csv_header(csv_path: str) -> tuple:
    """
    Validate CSV file header and extract date range
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        Tuple of (is_valid, start_date, end_date, message)
    """
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline().strip()
        
        start_date, end_date = extract_dates_from_header(first_line)
        
        if start_date is None or end_date is None:
            return False, None, None, "Could not extract dates from header"
        
        is_valid = validate_date_range_months(start_date, end_date, 3)
        
        if is_valid:
            message = f"Date range valid: {start_date.strftime('%d/%m/%Y %H:%M')} to {end_date.strftime('%d/%m/%Y %H:%M')} (>= 3 months)"
        else:
            delta = relativedelta(end_date, start_date)
            total_months = delta.years * 12 + delta.months
            message = f"Date range invalid: {start_date.strftime('%d/%m/%Y %H:%M')} to {end_date.strftime('%d/%m/%Y %H:%M')} ({total_months} months, required: >= 3 months)"
        
        return is_valid, start_date, end_date, message
        
    except Exception as e:
        return False, None, None, f"Error reading file: {e}"


def validate_csv_headers(csv_path: str) -> tuple:
    """
    Validate CSV file column headers (row 2)
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        Tuple of (is_valid, errors_list, message)
    """
    expected_headers = [
        "كود", "إسم الصنف", "سعر البيع", "الشركة", "الوحدة",
        "مبيعات الادارة", "متوسط مبيعات الادارة", "رصيد الادارة",
        "مبيعات الشهيد", "متوسط مبيعات الشهيد", "رصيد الشهيد",
        "مبيعات العشرين", "متوسط مبيعات العشرين", "رصيد العشرين",
        "مبيعات العقبى", "متوسط مبيعات العقبى", "رصيد العقبى",
        "مبيعات النجوم", "متوسط مبيعات النجوم", "رصيد النجوم",
        "مبيعات الوردانى", "متوسط مبيعات الوردانى", "رصيد الوردانى",
        "إجمالى المبيعات", "إجمالى رصيد الصنف"
    ]
    
    errors = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline().strip()
            
            start_date, end_date = extract_dates_from_header(first_line)
            if start_date and end_date:
                second_line = f.readline().strip()
            else:
                second_line = first_line
        
        if not second_line:
            return False, ["Header row is empty"], "Header row is empty"
        
        actual_headers = [col.strip() for col in second_line.split(',')]
        
        if len(actual_headers) != len(expected_headers):
            errors.append(f"Column count mismatch: Expected {len(expected_headers)} columns, found {len(actual_headers)}")
        
        min_len = min(len(actual_headers), len(expected_headers))
        
        for i in range(min_len):
            if actual_headers[i] != expected_headers[i]:
                errors.append(f"Column {i+1}: Expected '{expected_headers[i]}', found '{actual_headers[i]}'")
        
        if len(actual_headers) > len(expected_headers):
            for i in range(len(expected_headers), len(actual_headers)):
                errors.append(f"Extra column {i+1}: '{actual_headers[i]}'")
        
        if len(actual_headers) < len(expected_headers):
            for i in range(len(actual_headers), len(expected_headers)):
                errors.append(f"Missing column {i+1}: '{expected_headers[i]}'")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            message = "Column headers validation successful: All headers match expected order"
        else:
            message = f"Column headers validation failed: {len(errors)} error(s) found"
        
        return is_valid, errors, message
        
    except Exception as e:
        return False, [f"Error reading file: {e}"], f"Error reading file: {e}"

