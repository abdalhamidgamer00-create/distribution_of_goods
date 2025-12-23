"""Logging helpers for data validation."""

from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def log_date_validation(
    is_valid: bool, start_date, end_date, message: str
) -> None:
    """Log date range validation results."""
    logger.info("[1] Date Range Validation: %s", message)
    if start_date and end_date:
        logger.info(
            "    Start: %s, End: %s", 
            start_date.strftime('%d/%m/%Y %H:%M'),
            end_date.strftime('%d/%m/%Y %H:%M')
        )
    status = ">= 3 months" if is_valid else "less than 3 months"
    logger.info("    %s Date range is %s", "✓" if is_valid else "✗", status)


def log_headers_validation(is_valid: bool, errors: list, message: str) -> None:
    """Log column headers validation results."""
    logger.info("[2] Column Headers Validation: %s", message)
    if is_valid:
        logger.info("    ✓ All column headers match expected order")
    else:
        logger.warning("    ✗ Column headers validation failed:")
        for error in errors:
            logger.warning("      - %s", error)


def log_overall_result(is_valid: bool) -> None:
    """Log overall validation result."""
    logger.info("=" * 50)
    result = "SUCCESSFUL" if is_valid else "FAILED"
    logger.info(
        "%s Overall validation: %s", "✓" if is_valid else "✗", result
    )
    logger.info("=" * 50)
