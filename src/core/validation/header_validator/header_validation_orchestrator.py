"""Main header validation orchestrator."""

from src.core.validation.header_validator.header_validation_constants import (
    get_required_headers, get_optional_headers
)
from src.core.validation.header_validator.header_reader import read_header_line
from src.core.validation.header_validator.checks import check_all_headers


def validate_csv_headers(csv_path: str) -> tuple:
    """Validate CSV file column headers (row 2)."""
    required_headers = get_required_headers()
    optional_headers = get_optional_headers()
    
    try:
        return _try_validate_headers(
            csv_path, required_headers, optional_headers
        )
    except Exception as error:
        err_msg = f"Error reading file: {error}"
        return False, [err_msg], err_msg


def _try_validate_headers(
    csv_path: str, required_headers: list, optional_headers: list
) -> tuple:
    """Try to validate headers with error handling."""
    second_line = read_header_line(csv_path)
    if not second_line:
        return False, ["Header row is empty"], "Header row is empty"
    
    actual_headers = [column.strip() for column in second_line.split(',')]
    errors, warnings = check_all_headers(
        actual_headers, required_headers, optional_headers
    )
    return _build_validation_result(errors, warnings, len(required_headers))


def _build_validation_result(
    errors: list, warnings: list, required_count: int
) -> tuple:
    """Build validation result tuple."""
    is_valid = len(errors) == 0
    if is_valid:
        message = (
            f"✅ Column headers validation successful: "
            f"All {required_count} required columns present"
        )
        if warnings:
            warning_msg = "; ".join(warnings)
            message += f"\n⚠️ {len(warnings)} warning(s): {warning_msg}"
    else:
        message = (
            f"❌ Column headers validation failed: "
            f"{len(errors)} error(s) found"
        )
    return is_valid, errors, message
