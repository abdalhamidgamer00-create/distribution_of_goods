"""Main orchestrator for step 1."""

import os
from src.shared.utils.archiver import archive_all_output, clear_output_directory
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_1.cleaner.files import has_files_in_directory
from src.app.pipeline.step_1.cleaner.reporting import log_archive_summary

logger = get_logger(__name__)


def step_1_archive_output(use_latest_file: bool = None) -> bool:
    """Step 1: Archive previous output files before starting new process."""
    output_dir = os.path.join("data", "output")
    archive_base_dir = os.path.join("data", "archive")
    
    try:
        return _archive_if_has_files(output_dir, archive_base_dir)
    except Exception as error:
        logger.exception("Error during archiving: %s", error)
        return False


def _execute_archive(archive_base_dir: str, output_dir: str) -> bool:
    """Execute archive and clear output."""
    result = archive_all_output(archive_base_dir=archive_base_dir, create_zip=True)
    log_archive_summary(result, result['archive_dir'])
    
    clear_success = clear_output_directory(output_dir)
    status = (
        "✓ Output directory cleared successfully" 
        if clear_success else "⚠ Some files could not be deleted"
    )
    logger.info(status)
    return True


def _archive_if_has_files(output_dir: str, archive_base_dir: str) -> bool:
    """Archive if output directory has files."""
    if not has_files_in_directory(output_dir):
        logger.info("No previous output to archive. Starting fresh...")
        return True
    
    logger.info("Archiving previous output files...")
    return _execute_archive(archive_base_dir, output_dir)
