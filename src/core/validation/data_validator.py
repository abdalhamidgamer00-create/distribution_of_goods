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


def calculate_days_between(start_date: datetime, end_date: datetime) -> int:
    """
    Calculate number of days between two dates
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Number of days between dates (minimum 1 to avoid division by zero)
    """
    if start_date is None or end_date is None:
        return 0
    
    if end_date < start_date:
        return 0
    
    delta = end_date - start_date
    days = delta.days
    
    # Return at least 1 day to avoid division by zero
    return max(1, days)


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


def _read_header_line(csv_path: str) -> tuple:
    """Read and parse header line from CSV file."""
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        first_line = f.readline().strip()
        
        start_date, end_date = extract_dates_from_header(first_line)
        if start_date and end_date:
            second_line = f.readline().strip()
        else:
            second_line = first_line
    
    return second_line


def _get_required_headers() -> list:
    """Get list of required column headers."""
    return [
        "كود", "إسم الصنف", "سعر البيع", "الشركة", "الوحدة",
        "مبيعات الادارة", "رصيد الادارة",
        "مبيعات الشهيد", "رصيد الشهيد",
        "مبيعات العشرين", "رصيد العشرين",
        "مبيعات العقبى", "رصيد العقبى",
        "مبيعات النجوم", "رصيد النجوم",
        "مبيعات الوردانى", "رصيد الوردانى"
    ]


def _get_optional_headers() -> list:
    """Get list of optional column headers."""
    return [
        "متوسط مبيعات الادارة", "متوسط مبيعات الشهيد", "متوسط مبيعات العشرين",
        "متوسط مبيعات العقبى", "متوسط مبيعات النجوم", "متوسط مبيعات الوردانى",
        "إجمالى المبيعات", "إجمالى رصيد الصنف"
    ]


def _check_missing_required(actual_headers: list, required_headers: list) -> list:
    """Check for missing required columns."""
    return [req for req in required_headers if req not in actual_headers]


def _check_unknown_columns(actual_headers: list, required_headers: list, optional_headers: list) -> list:
    """Check for unknown columns not in required or optional."""
    all_known = required_headers + optional_headers
    return [h for h in actual_headers if h and h not in all_known]


def validate_csv_headers(csv_path: str) -> tuple:
    """
    Validate CSV file column headers (row 2).
    
    Returns:
        Tuple of (is_valid, errors_list, message)
    """
    required_headers = _get_required_headers()
    optional_headers = _get_optional_headers()
    errors = []
    warnings = []
    
    try:
        second_line = _read_header_line(csv_path)
        
        if not second_line:
            return False, ["Header row is empty"], "Header row is empty"
        
        actual_headers = [col.strip() for col in second_line.split(',')]
        
        # Check for required columns
        missing_required = _check_missing_required(actual_headers, required_headers)
        if missing_required:
            errors.append(f"Missing required columns: {', '.join(missing_required)}")
        
        # Check for unknown columns
        unknown_columns = _check_unknown_columns(actual_headers, required_headers, optional_headers)
        if unknown_columns:
            warnings.append(f"Unknown columns (will be ignored): {', '.join(unknown_columns[:5])}")
        
        # Check for optional columns
        present_optional = [col for col in optional_headers if col in actual_headers]
        if present_optional:
            warnings.append(f"Optional columns detected (will be recalculated): {len(present_optional)} columns")
        
        is_valid = len(errors) == 0
        
        if is_valid:
            message = f"✅ Column headers validation successful: All {len(required_headers)} required columns present"
            if warnings:
                message += f"\n⚠️ {len(warnings)} warning(s): " + "; ".join(warnings)
        else:
            message = f"❌ Column headers validation failed: {len(errors)} error(s) found"
        
        return is_valid, errors, message
        
    except Exception as e:
        return False, [f"Error reading file: {e}"], f"Error reading file: {e}"


