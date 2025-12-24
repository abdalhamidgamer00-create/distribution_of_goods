"""Directory operations for archiver."""

import os
import shutil
from datetime import datetime
from src.shared.utility.logging_utils import get_logger

logger = get_logger(__name__)


def count_directory_contents(directory: str) -> tuple:
    """Count files and directories in a path."""
    file_count = 0
    directory_count = 0
    for _, directories, files in os.walk(directory):
        directory_count += len(directories)
        file_count += len(files)
    return file_count, directory_count


def prepare_archive_directory(
    output_directory: str, 
    archive_base_dir: str
) -> tuple:
    """Prepare archive directory and paths."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = os.path.join(archive_base_dir, f"archive_{timestamp}")
    os.makedirs(archive_base_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)
    output_name = os.path.basename(output_directory.rstrip('/'))
    return archive_dir, os.path.join(archive_dir, output_name)


def copy_directory_tree(source: str, destination: str) -> None:
    """Copy complete directory tree, removing destination if exists."""
    if os.path.exists(destination):
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def archive_and_copy(output_directory: str, archive_output_dir: str) -> tuple:
    """Copy directory and return counts."""
    file_count, directory_count = count_directory_contents(output_directory)
    logger.info(
        "  Found %s files in %s directories", file_count, directory_count
    )
    
    if os.path.exists(output_directory):
        copy_directory_tree(output_directory, archive_output_dir)
    
    return count_directory_contents(archive_output_dir)
