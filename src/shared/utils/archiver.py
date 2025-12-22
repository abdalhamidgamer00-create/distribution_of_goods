"""Archive output files"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


# =============================================================================
# PUBLIC API
# =============================================================================

def archive_output_directory(output_directory: str, archive_base_dir: str = "data/archive") -> dict:
    """Archive ALL files and directories from output directory to a timestamped archive."""
    if not os.path.exists(output_directory):
        raise ValueError(f"Output directory not found: {output_directory}")
    archive_dir, archive_output_dir = _prepare_archive_directory(output_directory, archive_base_dir)
    logger.info("Archiving complete contents of %s...\n  Source: %s\n  Destination: %s", output_directory, output_directory, archive_output_dir)
    archived_file_count, archived_dir_count = _archive_and_copy(output_directory, archive_output_dir)
    return _log_archive_result(archive_dir, archived_file_count, archived_dir_count)


def create_zip_archive(archive_dir: str, zip_output_path: str = None) -> str:
    """Create a ZIP file from archive directory."""
    if not os.path.exists(archive_dir):
        raise ValueError(f"Archive directory not found: {archive_dir}")
    if zip_output_path is None:
        zip_output_path = f"{archive_dir}.zip"
    logger.info("Creating ZIP archive: %s...", zip_output_path)
    _write_zip_files(archive_dir, zip_output_path)
    logger.info("ZIP archive created successfully: %s", zip_output_path)
    return zip_output_path


def archive_all_output(archive_base_dir: str = "data/archive", create_zip: bool = True) -> dict:
    """Archive ALL contents of the output directory."""
    output_directory = "data/output"
    
    if not os.path.exists(output_directory):
        raise ValueError(f"Output directory not found: {output_directory}")
    
    archive_info = archive_output_directory(output_directory, archive_base_dir)
    zip_file = create_zip_archive(archive_info['archive_dir']) if create_zip else None
    return _build_archive_result(archive_info, zip_file)


def clear_output_directory(output_directory: str = "data/output") -> bool:
    """Clear all contents of the output directory after archiving."""
    if not os.path.exists(output_directory):
        logger.warning("Output directory not found: %s", output_directory)
        return True
    
    try:
        return _try_clear_directory(output_directory)
    except Exception as error:
        logger.exception("  ✗ Error clearing output directory: %s", error)
        return False


# =============================================================================
# DIRECTORY COUNTING HELPERS
# =============================================================================

def _count_directory_contents(directory: str) -> tuple:
    """Count files and directories in a path."""
    file_count = 0
    directory_count = 0
    for root, directories, files in os.walk(directory):
        directory_count += len(directories)
        file_count += len(files)
    return file_count, directory_count


# =============================================================================
# ARCHIVE PREPARATION HELPERS
# =============================================================================

def _prepare_archive_directory(output_directory: str, archive_base_dir: str) -> tuple:
    """Prepare archive directory and paths."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = os.path.join(archive_base_dir, f"archive_{timestamp}")
    os.makedirs(archive_base_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)
    output_name = os.path.basename(output_directory.rstrip('/'))
    return archive_dir, os.path.join(archive_dir, output_name)


def _copy_directory_tree(source: str, destination: str) -> None:
    """Copy complete directory tree, removing destination if exists."""
    if os.path.exists(destination):
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def _archive_and_copy(output_directory: str, archive_output_dir: str) -> tuple:
    """Copy directory and return counts."""
    file_count, directory_count = _count_directory_contents(output_directory)
    logger.info("  Found %s files in %s directories", file_count, directory_count)
    
    if os.path.exists(output_directory):
        _copy_directory_tree(output_directory, archive_output_dir)
    
    return _count_directory_contents(archive_output_dir)


# =============================================================================
# ARCHIVE RESULT HELPERS
# =============================================================================

def _log_archive_result(archive_dir: str, file_count: int, directory_count: int) -> dict:
    """Log archive results and return info dict."""
    logger.info("Archive created successfully!")
    logger.info("  - Archive location: %s", archive_dir)
    logger.info("  - Archived %s files in %s directories", file_count, directory_count)
    
    return {
        'archive_dir': archive_dir,
        'file_count': file_count,
        'dir_count': directory_count
    }


def _build_archive_result(archive_info: dict, zip_file: str = None) -> dict:
    """Build result dictionary from archive info."""
    return {
        'archive_dir': archive_info['archive_dir'],
        'file_count': archive_info.get('file_count', 0),
        'dir_count': archive_info.get('dir_count', 0),
        'zip_file': zip_file
    }


# =============================================================================
# ZIP FILE HELPERS
# =============================================================================

def _write_zip_files(archive_dir: str, zip_output_path: str) -> None:
    """Write all files from archive directory to ZIP file."""
    import zipfile
    
    with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as zip_handle:
        for root, directories, files in os.walk(archive_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                arcname = os.path.relpath(file_path, archive_dir)
                zip_handle.write(file_path, arcname)


# =============================================================================
# DIRECTORY CLEARING HELPERS
# =============================================================================

def _delete_directory_contents(directory: str) -> None:
    """Delete all contents of a directory but keep the directory itself."""
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        except Exception as error:
            logger.warning("  Warning: Could not delete %s: %s", item_path, error)


def _handle_empty_directory(file_count: int, directory_count: int) -> bool:
    """Handle case of empty directory."""
    if file_count == 0 and directory_count == 0:
        logger.info("  Output directory is already empty.")
        return True
    return None


def _delete_and_verify(output_directory: str, file_count: int, directory_count: int) -> bool:
    """Delete contents and verify result."""
    logger.info("  Found %s files in %s directories to delete", file_count, directory_count)
    _delete_directory_contents(output_directory)
    remaining_files, remaining_directories = _count_directory_contents(output_directory)
    if remaining_files == 0 and remaining_directories == 0:
        logger.info("  ✓ Output directory cleared successfully!\n  ✓ Deleted %s files and %s directories", file_count, directory_count)
        return True
    logger.warning("  ⚠ Some files/directories could not be deleted\n  Remaining: %s files, %s directories", remaining_files, remaining_directories)
    return False


def _try_clear_directory(output_directory: str) -> bool:
    """Try to clear directory contents."""
    logger.info("Clearing output directory: %s...", output_directory)
    file_count, directory_count = _count_directory_contents(output_directory)
    
    empty_result = _handle_empty_directory(file_count, directory_count)
    if empty_result is not None:
        return empty_result
    
    return _delete_and_verify(output_directory, file_count, directory_count)
