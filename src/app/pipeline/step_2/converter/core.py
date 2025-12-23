"""Core conversion logic."""

from src.services.conversion.converters.excel_to_csv import convert_excel_to_csv
from src.shared.utils.logging_utils import get_logger
from src.shared.utils.file_handler import get_file_path
from src.app.pipeline.step_2.converter.naming import generate_output_filename
from src.app.pipeline.step_2.converter.selection import validate_and_select

logger = get_logger(__name__)


def log_conversion_result(success: bool, converted_dir: str) -> None:
    """Log conversion result."""
    if success:
        logger.info("Conversion successful! File saved to: %s", converted_dir)
    else:
        logger.error("Conversion failed!")


def perform_conversion(excel_file: str, input_dir: str, converted_dir: str) -> bool:
    """Perform the CSV conversion."""
    csv_file = generate_output_filename(excel_file)
    logger.info("Converting %s to %s...", excel_file, csv_file)
    success = convert_excel_to_csv(get_file_path(excel_file, input_dir), get_file_path(csv_file, converted_dir))
    log_conversion_result(success, converted_dir)
    return success


def try_convert_excel(input_dir: str, converted_dir: str, use_latest_file: bool) -> bool:
    """Try to convert Excel with error handling."""
    excel_file = validate_and_select(input_dir, use_latest_file)
    return perform_conversion(excel_file, input_dir, converted_dir) if excel_file else False
