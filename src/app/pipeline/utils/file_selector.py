"""File selection utilities for pipeline steps"""

from src.shared.utils.file_handler import get_latest_file
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def select_csv_file(output_dir: str, csv_files: list, use_latest_file: bool = None) -> str:
    """
    Select CSV file based on user choice or use_latest_file flag.
    
    Args:
        output_dir: Directory containing CSV files
        csv_files: List of available CSV file names
        use_latest_file: True to use latest, False to select, None to ask user
        
    Returns:
        Selected CSV file name
        
    Raises:
        ValueError: If no files found or invalid selection
    """
    if use_latest_file is True:
        csv_file = get_latest_file(output_dir, '.csv')
        if not csv_file:
            raise ValueError("No CSV files found!")
        logger.info("Using latest file: %s", csv_file)
        return csv_file
    
    elif use_latest_file is False:
        logger.info("Available CSV files:")
        for idx, filename in enumerate(csv_files, 1):
            logger.info("  %s. %s", idx, filename)
        
        choice = input("\nSelect file number: ").strip()
        file_index = int(choice) - 1
        
        if file_index < 0 or file_index >= len(csv_files):
            raise ValueError("Invalid selection!")
        
        return csv_files[file_index]
    
    else:
        logger.info("Select file option:")
        logger.info("  1. Select specific file")
        logger.info("  2. Use latest file")
        
        option = input("\nSelect option (1 or 2): ").strip()
        
        if option == "2":
            csv_file = get_latest_file(output_dir, '.csv')
            if not csv_file:
                raise ValueError("No CSV files found!")
            logger.info("Using latest file: %s", csv_file)
            return csv_file
        
        elif option == "1":
            logger.info("Available CSV files:")
            for idx, filename in enumerate(csv_files, 1):
                logger.info("  %s. %s", idx, filename)
            
            choice = input("\nSelect file number: ").strip()
            file_index = int(choice) - 1
            
            if file_index < 0 or file_index >= len(csv_files):
                raise ValueError("Invalid selection!")
            
            return csv_files[file_index]
        
        else:
            raise ValueError("Invalid option!")


def select_excel_file(input_dir: str, excel_files: list, use_latest_file: bool = None) -> str:
    """
    Select Excel file based on user choice or use_latest_file flag.
    Supports both .xlsx and .xls formats.
    
    Args:
        input_dir: Directory containing Excel files
        excel_files: List of available Excel file names
        use_latest_file: True to use latest, False to select, None to ask user
        
    Returns:
        Selected Excel file name
        
    Raises:
        ValueError: If no files found or invalid selection
    """
    if use_latest_file is True:
        excel_file = get_latest_file(input_dir, '.xlsx')
        if not excel_file:
            excel_file = get_latest_file(input_dir, '.xls')
        if not excel_file:
            raise ValueError("No Excel files found!")
        logger.info("Using latest file: %s", excel_file)
        return excel_file
    
    elif use_latest_file is False:
        logger.info("Available Excel files:")
        for idx, filename in enumerate(excel_files, 1):
            logger.info("  %s. %s", idx, filename)
        
        choice = input("\nSelect file number: ").strip()
        file_index = int(choice) - 1
        
        if file_index < 0 or file_index >= len(excel_files):
            raise ValueError("Invalid selection!")
        
        return excel_files[file_index]
    
    else:
        logger.info("Select file option:")
        logger.info("  1. Select specific file")
        logger.info("  2. Use latest file")
        
        option = input("\nSelect option (1 or 2): ").strip()
        
        if option == "2":
            excel_file = get_latest_file(input_dir, '.xlsx')
            if not excel_file:
                excel_file = get_latest_file(input_dir, '.xls')
            if not excel_file:
                raise ValueError("No Excel files found!")
            logger.info("Using latest file: %s", excel_file)
            return excel_file
        
        elif option == "1":
            logger.info("Available Excel files:")
            for idx, filename in enumerate(excel_files, 1):
                logger.info("  %s. %s", idx, filename)
            
            choice = input("\nSelect file number: ").strip()
            file_index = int(choice) - 1
            
            if file_index < 0 or file_index >= len(excel_files):
                raise ValueError("Invalid selection!")
            
            return excel_files[file_index]
        
        else:
            raise ValueError("Invalid option!")

