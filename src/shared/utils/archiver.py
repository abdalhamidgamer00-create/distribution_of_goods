"""Archive output files"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _count_directory_contents(directory: str) -> tuple:
    """Count files and directories in a path."""
    file_count = 0
    dir_count = 0
    for root, dirs, files in os.walk(directory):
        dir_count += len(dirs)
        file_count += len(files)
    return file_count, dir_count


def _copy_directory_tree(source: str, destination: str) -> None:
    """Copy complete directory tree, removing destination if exists."""
    if os.path.exists(destination):
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def _prepare_archive_directory(output_dir: str, archive_base_dir: str) -> tuple:
    """Prepare archive directory and paths."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = os.path.join(archive_base_dir, f"archive_{timestamp}")
    
    os.makedirs(archive_base_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)
    
    output_name = os.path.basename(output_dir.rstrip('/'))
    archive_output_dir = os.path.join(archive_dir, output_name)
    
    return archive_dir, archive_output_dir


def _log_archive_result(archive_dir: str, file_count: int, dir_count: int) -> dict:
    """Log archive results and return info dict."""
    logger.info("Archive created successfully!")
    logger.info("  - Archive location: %s", archive_dir)
    logger.info("  - Archived %s files in %s directories", file_count, dir_count)
    
    return {
        'archive_dir': archive_dir,
        'file_count': file_count,
        'dir_count': dir_count
    }


def archive_output_directory(output_dir: str, archive_base_dir: str = "data/archive") -> dict:
    """Archive ALL files and directories from output directory to a timestamped archive."""
    if not os.path.exists(output_dir):
        raise ValueError(f"Output directory not found: {output_dir}")
    
    archive_dir, archive_output_dir = _prepare_archive_directory(output_dir, archive_base_dir)
    
    logger.info("Archiving complete contents of %s...", output_dir)
    logger.info("  Source: %s", output_dir)
    logger.info("  Destination: %s", archive_output_dir)
    
    file_count, dir_count = _count_directory_contents(output_dir)
    logger.info("  Found %s files in %s directories", file_count, dir_count)
    
    if os.path.exists(output_dir):
        _copy_directory_tree(output_dir, archive_output_dir)
    
    archived_file_count, archived_dir_count = _count_directory_contents(archive_output_dir)
    
    return _log_archive_result(archive_dir, archived_file_count, archived_dir_count)



def create_zip_archive(archive_dir: str, zip_output_path: str = None) -> str:
    """
    Create a ZIP file from archive directory
    
    Args:
        archive_dir: Directory to compress
        zip_output_path: Optional path for ZIP file (default: archive_dir + .zip)
        
    Returns:
        Path to the created ZIP file
    """
    import zipfile
    
    if not os.path.exists(archive_dir):
        raise ValueError(f"Archive directory not found: {archive_dir}")
    
    if zip_output_path is None:
        zip_output_path = f"{archive_dir}.zip"
    
    logger.info("Creating ZIP archive: %s...", zip_output_path)
    
    with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(archive_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, archive_dir)
                zipf.write(file_path, arcname)
    
    logger.info("ZIP archive created successfully: %s", zip_output_path)
    
    return zip_output_path


def _build_archive_result(archive_info: dict, zip_file: str = None) -> dict:
    """Build result dictionary from archive info."""
    return {
        'archive_dir': archive_info['archive_dir'],
        'file_count': archive_info.get('file_count', 0),
        'dir_count': archive_info.get('dir_count', 0),
        'zip_file': zip_file
    }


def archive_all_output(archive_base_dir: str = "data/archive", create_zip: bool = True) -> dict:
    """Archive ALL contents of the output directory."""
    output_dir = "data/output"
    
    if not os.path.exists(output_dir):
        raise ValueError(f"Output directory not found: {output_dir}")
    
    archive_info = archive_output_directory(output_dir, archive_base_dir)
    zip_file = create_zip_archive(archive_info['archive_dir']) if create_zip else None
    return _build_archive_result(archive_info, zip_file)


def _delete_directory_contents(directory: str) -> None:
    """Delete all contents of a directory but keep the directory itself."""
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        except Exception as e:
            logger.warning("  Warning: Could not delete %s: %s", item_path, e)


def _handle_empty_directory(file_count: int, dir_count: int) -> bool:
    """Handle case of empty directory."""
    if file_count == 0 and dir_count == 0:
        logger.info("  Output directory is already empty.")
        return True
    return None


def _delete_and_verify(output_dir: str, file_count: int, dir_count: int) -> bool:
    """Delete contents and verify result."""
    logger.info("  Found %s files in %s directories to delete", file_count, dir_count)
    _delete_directory_contents(output_dir)
    
    remaining_files, remaining_dirs = _count_directory_contents(output_dir)
    if remaining_files == 0 and remaining_dirs == 0:
        logger.info("  ✓ Output directory cleared successfully!")
        logger.info("  ✓ Deleted %s files and %s directories", file_count, dir_count)
        return True
    
    logger.warning("  ⚠ Some files/directories could not be deleted")
    logger.warning("  Remaining: %s files, %s directories", remaining_files, remaining_dirs)
    return False


def clear_output_directory(output_dir: str = "data/output") -> bool:
    """Clear all contents of the output directory after archiving."""
    if not os.path.exists(output_dir):
        logger.warning("Output directory not found: %s", output_dir)
        return True
    
    try:
        logger.info("Clearing output directory: %s...", output_dir)
        file_count, dir_count = _count_directory_contents(output_dir)
        
        empty_result = _handle_empty_directory(file_count, dir_count)
        if empty_result is not None:
            return empty_result
        
        return _delete_and_verify(output_dir, file_count, dir_count)
    except Exception as e:
        logger.exception("  ✗ Error clearing output directory: %s", e)
        return False


