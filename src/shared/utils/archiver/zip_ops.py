"""ZIP file operations for archiver."""

import os
import zipfile
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def write_zip_files(archive_dir: str, zip_output_path: str) -> None:
    """Write all files from archive directory to ZIP file."""
    with zipfile.ZipFile(
        zip_output_path, 'w', zipfile.ZIP_DEFLATED
    ) as zip_handle:
        for root, _, files in os.walk(archive_dir):
            for filename in files:
                file_path = os.path.join(root, filename)
                arcname = os.path.relpath(file_path, archive_dir)
                zip_handle.write(file_path, arcname)


def create_zip_archive(archive_dir: str, zip_output_path: str = None) -> str:
    """Create a ZIP file from archive directory."""
    if not os.path.exists(archive_dir):
        raise ValueError(f"Archive directory not found: {archive_dir}")
    if zip_output_path is None:
        zip_output_path = f"{archive_dir}.zip"
    logger.info("Creating ZIP archive: %s...", zip_output_path)
    write_zip_files(archive_dir, zip_output_path)
    logger.info("ZIP archive created successfully: %s", zip_output_path)
    return zip_output_path
