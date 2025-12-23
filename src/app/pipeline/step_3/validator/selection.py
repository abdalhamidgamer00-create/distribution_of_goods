"""File selection and try/catch handlers."""

from src.shared.utils.logging_utils import get_logger
from src.shared.utils.file_handler import get_file_path
from src.app.pipeline.utils.file_selector import select_csv_file
from src.app.pipeline.step_3.validator import validation

logger = get_logger(__name__)


def validate_csv_file(
    output_dir: str, csv_files: list, use_latest_file: bool
) -> bool:
    """Validate a selected CSV file."""
    csv_file = select_csv_file(output_dir, csv_files, use_latest_file)
    csv_path = get_file_path(csv_file, output_dir)
    
    logger.info("Validating %s...", csv_file)
    logger.info("-" * 50)
    
    overall_valid = validation.perform_validation(csv_path)
    return validation.handle_post_validation(
        overall_valid, csv_path, csv_file
    )


def try_validate(
    output_dir: str, csv_files: list, use_latest_file: bool
) -> bool:
    """Try to validate files with error handling."""
    try:
        return validate_csv_file(output_dir, csv_files, use_latest_file)
    except ValueError:
        logger.error("Invalid input! Please enter a number.")
        return False
    except Exception as error:
        logger.exception("Error during validation: %s", error)
        return False
