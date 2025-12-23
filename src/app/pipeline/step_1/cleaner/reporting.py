"""Reporting and logging helpers."""

import os
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_1.cleaner.files import calculate_directory_size
from src.app.pipeline.step_1.cleaner.formatting import format_size

logger = get_logger(__name__)


def log_zip_info(zip_file: str, archive_size: int) -> None:
    """Log ZIP file information."""
    if zip_file and os.path.exists(zip_file):
        zip_size = os.path.getsize(zip_file)
        compression_ratio = (
            (1 - zip_size / archive_size) * 100 if archive_size > 0 else 0
        )
        logger.info(
            "ZIP: %s (%.1f%% compression)", 
            format_size(zip_size), 
            compression_ratio
        )


def log_archive_summary(result: dict, archive_dir: str) -> None:
    """Log archive creation summary."""
    archive_size = calculate_directory_size(archive_dir)
    logger.info(
        "Archive created: %s files, %s dirs | Size: %s", 
        result.get("file_count", 0), 
        result.get("dir_count", 0), 
        format_size(archive_size)
    )
    log_zip_info(result.get('zip_file'), archive_size)
