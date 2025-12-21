"""Step 1: Archive previous output files handler"""

import os
from src.shared.utils.archiver import archive_all_output, clear_output_directory
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _has_files_in_directory(directory: str) -> bool:
    """Check if directory exists and has any files."""
    if not os.path.exists(directory):
        return False
    
    try:
        for root, dirs, files in os.walk(directory):
            if files:
                return True
    except Exception:
        pass
    return False


def _log_archive_summary(result: dict, archive_dir: str) -> None:
    """Log archive creation summary."""
    archive_size = _calculate_directory_size(archive_dir)
    
    logger.info("Archive created: %s files, %s dirs | Size: %s", 
               result.get("file_count", 0), 
               result.get("dir_count", 0),
               _format_size(archive_size))
    
    zip_file = result.get('zip_file')
    if zip_file and os.path.exists(zip_file):
        zip_size = os.path.getsize(zip_file)
        compression_ratio = (1 - zip_size / archive_size) * 100 if archive_size > 0 else 0
        logger.info("ZIP: %s (%.1f%% compression)", _format_size(zip_size), compression_ratio)


def step_1_archive_output(use_latest_file: bool = None) -> bool:
    """Step 1: Archive previous output files before starting new process."""
    output_dir = os.path.join("data", "output")
    archive_base_dir = os.path.join("data", "archive")
    
    if not _has_files_in_directory(output_dir):
        logger.info("No previous output to archive. Starting fresh...")
        return True
    
    try:
        logger.info("Archiving previous output files...")
        
        result = archive_all_output(archive_base_dir=archive_base_dir, create_zip=True)
        _log_archive_summary(result, result['archive_dir'])
        
        clear_success = clear_output_directory(output_dir)
        status = "✓ Output directory cleared successfully" if clear_success else "⚠ Some files could not be deleted"
        logger.info(status)
        
        return True
        
    except Exception as e:
        logger.exception("Error during archiving: %s", e)
        return False


def _calculate_directory_size(directory: str) -> int:
    """Calculate total size of directory in bytes"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception:
        pass
    return total_size


def _format_size(size_bytes: int) -> str:
    """Format size in bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

