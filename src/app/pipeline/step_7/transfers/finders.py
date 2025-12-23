"""File discovery logic for transfer generation."""

import os
from src.shared.utils.file_handler import get_csv_files, get_latest_file
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_7.transfers import validators

logger = get_logger(__name__)


def get_analytics_files(analytics_dir: str, branches: list) -> dict:
    """Get analytics files for all branches."""
    analytics_files = {}
    for branch in branches:
        branch_files = get_csv_files(os.path.join(analytics_dir, branch))
        if branch_files:
            analytics_files[branch] = branch_files
    return analytics_files


def validate_and_get_files(analytics_dir: str, branches: list) -> dict:
    """Validate and get analytics files."""
    if not validators.validate_analytics_directories(analytics_dir, branches):
        return None
    
    analytics_files = get_analytics_files(analytics_dir, branches)
    if not analytics_files:
        logger.error("No analytics files found in %s", analytics_dir)
        logger.error(
            "Please run step 5 (Split by Branches) first to generate "
            "analytics files"
        )
        return None
    return analytics_files


def try_extract_date_header(analytics_dir: str, analytics_files: dict) -> tuple:
    """Try to extract date header from analytics file."""
    first_branch = list(analytics_files.keys())[0]
    latest_file = get_latest_file(
        os.path.join(analytics_dir, first_branch), '.csv'
    )
    if not latest_file:
        return None
    
    sample_path = os.path.join(analytics_dir, first_branch, latest_file)
    with open(sample_path, 'r', encoding='utf-8-sig') as file_handle:
        first_line = file_handle.readline().strip()
        from src.core.validation import extract_dates_from_header
        start_date, end_date = extract_dates_from_header(first_line)
        return (True, first_line) if start_date and end_date else None


def extract_date_header_info(
    analytics_dir: str, 
    analytics_files: dict
) -> tuple:
    """Extract date header information from first analytics file."""
    try:
        result = try_extract_date_header(analytics_dir, analytics_files)
        return result if result else (False, "")
    except Exception:
        return False, ""
