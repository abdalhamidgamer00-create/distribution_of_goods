"""Directory cleanup operations for archiver."""

import os
import shutil
from src.shared.utils.logging_utils import get_logger
from src.shared.utils.archiver import directory_ops

logger = get_logger(__name__)


def delete_directory_contents(directory: str) -> None:
    """Delete all contents of a directory but keep the directory itself."""
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        except Exception as error:
            logger.warning(
                "  Warning: Could not delete %s: %s", item_path, error
            )


def handle_empty_directory(file_count: int, directory_count: int) -> bool:
    """Handle case of empty directory."""
    if file_count == 0 and directory_count == 0:
        logger.info("  Output directory is already empty.")
        return True
    return None


def delete_and_verify(
    output_directory: str, 
    file_count: int, 
    directory_count: int
) -> bool:
    """Delete contents and verify result."""
    logger.info(
        "  Found %s files in %s directories to delete", 
        file_count, 
        directory_count
    )
    delete_directory_contents(output_directory)
    remaining_files, remaining_directories = (
        directory_ops.count_directory_contents(output_directory)
    )
    if remaining_files == 0 and remaining_directories == 0:
        logger.info(
            "  ✓ Output directory cleared successfully!\n"
            "  ✓ Deleted %s files and %s directories", 
            file_count, 
            directory_count
        )
        return True
    logger.warning(
        "  ⚠ Some files/directories could not be deleted\n"
        "  Remaining: %s files, %s directories", 
        remaining_files, 
        remaining_directories
    )
    return False


def try_clear_directory(output_directory: str) -> bool:
    """Try to clear directory contents."""
    logger.info("Clearing output directory: %s...", output_directory)
    file_count, directory_count = directory_ops.count_directory_contents(
        output_directory
    )
    
    empty_result = handle_empty_directory(file_count, directory_count)
    if empty_result is not None:
        return empty_result
    
    return delete_and_verify(output_directory, file_count, directory_count)


def clear_output_directory(output_directory: str = "data/output") -> bool:
    """Clear all contents of the output directory after archiving."""
    if not os.path.exists(output_directory):
        logger.warning("Output directory not found: %s", output_directory)
        return True
    
    try:
        return try_clear_directory(output_directory)
    except Exception as error:
        logger.exception("  ✗ Error clearing output directory: %s", error)
        return False
