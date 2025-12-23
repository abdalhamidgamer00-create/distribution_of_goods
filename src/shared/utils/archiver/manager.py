"""Archiver manager and aggregation logic."""

import os
from src.shared.utils.logging_utils import get_logger
from src.shared.utils.archiver import directory_ops, zip_ops

logger = get_logger(__name__)


def log_archive_result(
    archive_dir: str, 
    file_count: int, 
    directory_count: int
) -> dict:
    """Log archive results and return info dict."""
    logger.info("Archive created successfully!")
    logger.info("  - Archive location: %s", archive_dir)
    logger.info(
        "  - Archived %s files in %s directories", file_count, directory_count
    )
    
    return {
        'archive_dir': archive_dir,
        'file_count': file_count,
        'dir_count': directory_count
    }


def build_archive_result(archive_info: dict, zip_file: str = None) -> dict:
    """Build result dictionary from archive info."""
    return {
        'archive_dir': archive_info['archive_dir'],
        'file_count': archive_info.get('file_count', 0),
        'dir_count': archive_info.get('dir_count', 0),
        'zip_file': zip_file
    }


def archive_output_directory(
    output_directory: str, 
    archive_base_dir: str = "data/archive"
) -> dict:
    """Archive ALL files from output directory to a timestamped archive."""
    if not os.path.exists(output_directory):
        raise ValueError(f"Output directory not found: {output_directory}")
    
    archive_dir, archive_output_dir = directory_ops.prepare_archive_directory(
        output_directory, archive_base_dir
    )
    
    logger.info(
        "Archiving complete contents of %s...\n"
        "  Source: %s\n  Destination: %s", 
        output_directory, 
        output_directory, 
        archive_output_dir
    )
    
    archived_file_count, archived_dir_count = directory_ops.archive_and_copy(
        output_directory, archive_output_dir
    )
    
    return log_archive_result(
        archive_dir, archived_file_count, archived_dir_count
    )


def archive_all_output(
    archive_base_dir: str = "data/archive", 
    create_zip: bool = True
) -> dict:
    """Archive ALL contents of the output directory."""
    output_directory = "data/output"
    
    if not os.path.exists(output_directory):
        raise ValueError(f"Output directory not found: {output_directory}")
    
    archive_info = archive_output_directory(output_directory, archive_base_dir)
    
    zip_file = None
    if create_zip:
        zip_file = zip_ops.create_zip_archive(archive_info['archive_dir'])
        
    return build_archive_result(archive_info, zip_file)
