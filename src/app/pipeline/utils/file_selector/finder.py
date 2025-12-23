"""File finding utilities."""

from src.shared.utils.file_handler import get_latest_file
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def get_latest_file_with_extensions(directory: str, extensions: list) -> str:
    """Get latest file matching any of the given extensions."""
    for extension in extensions:
        filename = get_latest_file(directory, extension)
        if filename:
            return filename
    return None


def get_latest_csv(output_dir: str) -> str:
    """Get latest CSV file or raise error."""
    csv_file = get_latest_file(output_dir, '.csv')
    if not csv_file:
        raise ValueError("No CSV files found!")
    logger.info("Using latest file: %s", csv_file)
    return csv_file


def get_latest_excel(input_dir: str) -> str:
    """Get latest Excel file or raise error."""
    excel_file = get_latest_file_with_extensions(input_dir, ['.xlsx', '.xls'])
    if not excel_file:
        raise ValueError("No Excel files found!")
    logger.info("Using latest file: %s", excel_file)
    return excel_file
