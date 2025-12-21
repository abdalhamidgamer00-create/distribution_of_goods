"""File selection utilities for pipeline steps"""

from src.shared.utils.file_handler import get_latest_file
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _get_latest_file_with_extensions(directory: str, extensions: list) -> str:
    """Get latest file matching any of the given extensions."""
    for ext in extensions:
        file = get_latest_file(directory, ext)
        if file:
            return file
    return None


def _show_files_list(files: list, file_type: str) -> None:
    """Display numbered list of files."""
    logger.info("Available %s files:", file_type)
    for idx, filename in enumerate(files, 1):
        logger.info("  %s. %s", idx, filename)


def _select_from_list(files: list) -> str:
    """Get file selection from user input."""
    choice = input("\nSelect file number: ").strip()
    file_index = int(choice) - 1
    
    if file_index < 0 or file_index >= len(files):
        raise ValueError("Invalid selection!")
    
    return files[file_index]


def _select_file_interactive(directory: str, files: list, extensions: list, file_type: str) -> str:
    """Handle interactive file selection when use_latest_file is None."""
    logger.info("Select file option:")
    logger.info("  1. Select specific file")
    logger.info("  2. Use latest file")
    
    option = input("\nSelect option (1 or 2): ").strip()
    
    if option == "2":
        file = _get_latest_file_with_extensions(directory, extensions)
        if not file:
            raise ValueError(f"No {file_type} files found!")
        logger.info("Using latest file: %s", file)
        return file
    
    elif option == "1":
        _show_files_list(files, file_type)
        return _select_from_list(files)
    
    else:
        raise ValueError("Invalid option!")


def select_csv_file(output_dir: str, csv_files: list, use_latest_file: bool = None) -> str:
    """
    Select CSV file based on user choice or use_latest_file flag.
    
    Returns:
        Selected CSV file name
    """
    if use_latest_file is True:
        csv_file = get_latest_file(output_dir, '.csv')
        if not csv_file:
            raise ValueError("No CSV files found!")
        logger.info("Using latest file: %s", csv_file)
        return csv_file
    
    elif use_latest_file is False:
        _show_files_list(csv_files, "CSV")
        return _select_from_list(csv_files)
    
    else:
        return _select_file_interactive(output_dir, csv_files, ['.csv'], "CSV")


def select_excel_file(input_dir: str, excel_files: list, use_latest_file: bool = None) -> str:
    """
    Select Excel file based on user choice or use_latest_file flag.
    
    Returns:
        Selected Excel file name
    """
    if use_latest_file is True:
        excel_file = _get_latest_file_with_extensions(input_dir, ['.xlsx', '.xls'])
        if not excel_file:
            raise ValueError("No Excel files found!")
        logger.info("Using latest file: %s", excel_file)
        return excel_file
    
    elif use_latest_file is False:
        _show_files_list(excel_files, "Excel")
        return _select_from_list(excel_files)
    
    else:
        return _select_file_interactive(input_dir, excel_files, ['.xlsx', '.xls'], "Excel")


