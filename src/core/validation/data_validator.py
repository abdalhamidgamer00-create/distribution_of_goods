"""Data validation utilities"""

import re
from datetime import datetime
from dateutil.relativedelta import relativedelta


# =============================================================================
# PUBLIC API
# =============================================================================

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


def validate_csv_headers(csv_path: str) -> tuple:
    """Validate CSV file column headers (row 2)."""
    required_headers = _get_required_headers()
    optional_headers = _get_optional_headers()
    
    try:
        return _try_validate_headers(csv_path, required_headers, optional_headers)
    except Exception as error:
        return False, [f"Error reading file: {error}"], f"Error reading file: {error}"


# =============================================================================
# DATE PARSING HELPERS
# =============================================================================

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


# =============================================================================
# DATE VALIDATION HELPERS
# =============================================================================

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


# =============================================================================
# HEADER CONFIGURATION
# =============================================================================

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


# =============================================================================
# HEADER VALIDATION HELPERS
# =============================================================================

def _read_header_line(csv_path: str) -> tuple:
    """Read and parse header line from CSV file."""
    with open(csv_path, 'r', encoding='utf-8-sig') as file_handle:
        first_line = file_handle.readline().strip()
        start_date, end_date = extract_dates_from_header(first_line)
        second_line = file_handle.readline().strip() if start_date and end_date else first_line
    return second_line


def _try_validate_headers(csv_path: str, required_headers: list, optional_headers: list) -> tuple:
    """Try to validate headers with error handling."""
    second_line = _read_header_line(csv_path)
    if not second_line:
        return False, ["Header row is empty"], "Header row is empty"
    
    actual_headers = [column.strip() for column in second_line.split(',')]
    errors, warnings = _check_all_headers(actual_headers, required_headers, optional_headers)
    return _build_validation_result(errors, warnings, len(required_headers))


def _check_all_headers(actual_headers: list, required_headers: list, optional_headers: list) -> tuple:
    """Check all headers and return errors and warnings."""
    errors, warnings = [], []
    _add_missing_error(errors, actual_headers, required_headers)
    _add_unknown_warning(warnings, actual_headers, required_headers, optional_headers)
    
    optional_warning = _check_optional_present(actual_headers, optional_headers)
    if optional_warning:
        warnings.append(optional_warning)
    
    return errors, warnings


# =============================================================================
# HEADER CHECK HELPERS
# =============================================================================

def _check_missing_required(actual_headers: list, required_headers: list) -> list:
    """Check for missing required columns."""
    return [required for required in required_headers if required not in actual_headers]


def _check_unknown_columns(actual_headers: list, required_headers: list, optional_headers: list) -> list:
    """Check for unknown columns not in required or optional."""
    all_known = required_headers + optional_headers
    return [header for header in actual_headers if header and header not in all_known]


def _check_optional_present(actual_headers: list, optional_headers: list) -> str:
    """Check for present optional columns and return warning if any."""
    present_optional = [column for column in optional_headers if column in actual_headers]
    if present_optional:
        return f"Optional columns detected (will be recalculated): {len(present_optional)} columns"
    return None


def _add_missing_error(errors: list, actual_headers: list, required_headers: list) -> None:
    """Add error for missing required columns."""
    missing_required = _check_missing_required(actual_headers, required_headers)
    if missing_required:
        errors.append(f"Missing required columns: {', '.join(missing_required)}")


def _add_unknown_warning(warnings: list, actual_headers: list, required_headers: list, optional_headers: list) -> None:
    """Add warning for unknown columns."""
    unknown_columns = _check_unknown_columns(actual_headers, required_headers, optional_headers)
    if unknown_columns:
        warnings.append(f"Unknown columns (will be ignored): {', '.join(unknown_columns[:5])}")


# =============================================================================
# RESULT BUILDING HELPERS
# =============================================================================

def _build_validation_result(errors: list, warnings: list, required_count: int) -> tuple:
    """Build validation result tuple."""
    is_valid = len(errors) == 0
    if is_valid:
        message = f"✅ Column headers validation successful: All {required_count} required columns present"
        if warnings:
            message += f"\n⚠️ {len(warnings)} warning(s): " + "; ".join(warnings)
    else:
        message = f"❌ Column headers validation failed: {len(errors)} error(s) found"
    return is_valid, errors, message
