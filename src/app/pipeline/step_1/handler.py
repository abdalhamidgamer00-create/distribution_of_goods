"""Step 1: Archive previous output files handler"""

import os
from src.shared.utils.archiver import archive_all_output, clear_output_directory
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def step_1_archive_output(use_latest_file: bool = None) -> bool:
    """Step 1: Archive previous output files before starting new process"""
    output_dir = os.path.join("data", "output")
    archive_base_dir = os.path.join("data", "archive")
    
    # Check if output directory exists and has files
    if not os.path.exists(output_dir):
        logger.info("No previous output to archive. Starting fresh...")
        return True
    
    has_files = False
    try:
        for root, dirs, files in os.walk(output_dir):
            if files:
                has_files = True
                break
    except Exception:
        pass
    
    if not has_files:
        logger.info("No previous output to archive. Starting fresh...")
        return True
    
    try:
        logger.info("Archiving previous output files...")
        
        # Archive all output files
        result = archive_all_output(archive_base_dir=archive_base_dir, create_zip=True)
        
        # Calculate archive size
        archive_size = _calculate_directory_size(result['archive_dir'])
        zip_size = os.path.getsize(result['zip_file']) if result.get('zip_file') and os.path.exists(result['zip_file']) else 0
        
        # Display concise summary
        logger.info("Archive created: %s files, %s dirs | Size: %s", 
                   result.get("file_count", 0), 
                   result.get("dir_count", 0),
                   _format_size(archive_size))
        if zip_size > 0:
            compression_ratio = (1 - zip_size / archive_size) * 100 if archive_size > 0 else 0
            logger.info("ZIP: %s (%.1f%% compression)", _format_size(zip_size), compression_ratio)
        
        # Clear output directory
        clear_success = clear_output_directory(output_dir)
        if clear_success:
            logger.info("✓ Output directory cleared successfully")
        else:
            logger.warning("⚠ Some files could not be deleted from output directory")
        
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

