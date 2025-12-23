"""Validation logic."""

from src.core.validation import validate_csv_header, validate_csv_headers
from src.app.pipeline.step_3.validator import logging, modification


def perform_validation(csv_path: str) -> tuple:
    """Perform date and headers validation."""
    is_valid_date, start_date, end_date, date_message = validate_csv_header(
        csv_path
    )
    logging.log_date_validation(
        is_valid_date, start_date, end_date, date_message
    )
    
    is_valid_headers, errors, headers_message = validate_csv_headers(csv_path)
    logging.log_headers_validation(is_valid_headers, errors, headers_message)
    
    return is_valid_date and is_valid_headers


def handle_post_validation(
    overall_valid: bool, csv_path: str, csv_file: str
) -> bool:
    """Handle post-validation actions."""
    logging.log_overall_result(overall_valid)
    
    if overall_valid and not modification.remove_first_row(csv_path, csv_file):
        return False
    return overall_valid
