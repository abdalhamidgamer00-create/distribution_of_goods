"""Date resolution and validation."""

from src.core.validation import extract_dates_from_header, calculate_days_between
from src.shared.utils.logging_utils import get_logger
from src.services.splitting.processors.data_preparer.constants import (
    DEFAULT_DAYS_FOR_AVG_SALES
)

logger = get_logger(__name__)


def resolve_date_range(first_line: str, start_date, end_date) -> tuple:
    """Resolve date range from parameters or header."""
    extracted_start, extracted_end = extract_dates_from_header(first_line)
    header_contained_dates = bool(extracted_start and extracted_end)
    
    return (
        start_date or extracted_start, 
        end_date or extracted_end, 
        header_contained_dates
    )


def raise_date_error_if_required(has_date_info: bool, require_dates: bool) -> None:
    """Raise error if dates are required but missing."""
    if require_dates and not has_date_info:
        raise ValueError(
            "❌ خطأ: لم يتم العثور على معلومات التاريخ!\n"
            "يجب توفير التواريخ إما:\n"
            "1. في السطر الأول من الملف بالصيغة: من: DD/MM/YYYY HH:MM إلى: DD/MM/YYYY HH:MM\n"
            "2. أو تمريرها كمعاملات (start_date, end_date)"
        )


def calculate_and_validate_days(start_date, end_date) -> int:
    """Calculate days and validate the result."""
    num_days = calculate_days_between(start_date, end_date)
    if num_days <= 0:
        raise ValueError(
            f"❌ خطأ: نطاق التاريخ غير صالح!\n"
            f"تاريخ البداية: {start_date}\n"
            f"تاريخ النهاية: {end_date}"
        )
    logger.info(f"✅ Date range: {num_days} days from {start_date} to {end_date}")
    return num_days


def validate_date_range(start_date, end_date, require_dates: bool) -> int:
    """Validate date range and calculate number of days."""
    has_date_info = bool(start_date and end_date)
    raise_date_error_if_required(has_date_info, require_dates)
    
    if has_date_info:
        return calculate_and_validate_days(start_date, end_date)
    
    logger.warning(
        f"⚠️ No date information found. Using default: {DEFAULT_DAYS_FOR_AVG_SALES} days"
    )
    return DEFAULT_DAYS_FOR_AVG_SALES
