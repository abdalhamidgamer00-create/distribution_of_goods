"""User interaction utilities."""

from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.utils.file_selector.finder import (
    get_latest_file_with_extensions
)

logger = get_logger(__name__)


def show_files_list(files: list, file_type: str) -> None:
    """Display numbered list of files."""
    logger.info("Available %s files:", file_type)
    for file_index, filename in enumerate(files, 1):
        logger.info("  %s. %s", file_index, filename)


def select_from_list(files: list) -> str:
    """Get file selection from user input."""
    choice = input("\nSelect file number: ").strip()
    try:
        file_index = int(choice) - 1
    except ValueError:
        raise ValueError("Invalid selection!")
    
    if file_index < 0 or file_index >= len(files):
        raise ValueError("Invalid selection!")
    
    return files[file_index]


def handle_option_choice(
    option: str, directory: str, files: list, extensions: list, file_type: str
) -> str:
    """Handle user option choice for file selection."""
    if option == "2":
        filename = get_latest_file_with_extensions(directory, extensions)
        if not filename:
            raise ValueError(f"No {file_type} files found!")
        logger.info("Using latest file: %s", filename)
        return filename
    elif option == "1":
        show_files_list(files, file_type)
        return select_from_list(files)
    else:
        raise ValueError("Invalid option!")


def select_file_interactive(
    directory: str, files: list, extensions: list, file_type: str
) -> str:
    """Handle interactive file selection when use_latest_file is None."""
    logger.info("Select file option:")
    logger.info("  1. Select specific file")
    logger.info("  2. Use latest file")
    
    option = input("\nSelect option (1 or 2): ").strip()
    return handle_option_choice(option, directory, files, extensions, file_type)
