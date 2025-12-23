"""Transfer generation execution logic."""

import os
from src.services.transfers.generators.transfer_generator import (
    generate_transfer_files
)
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_7.transfers import finders

logger = get_logger(__name__)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def group_files_by_source(transfer_files: dict) -> dict:
    """Group transfer files by source branch."""
    files_by_source = {}
    for (source, target), file_path in transfer_files.items():
        if source not in files_by_source:
            files_by_source[source] = []
        files_by_source[source].append((target, file_path))
    return files_by_source


def log_source_files(source: str, files_list: list) -> None:
    """Log files for a single source branch."""
    logger.info("\n  From %s (%d files):", source, len(files_list))
    for target, file_path in sorted(files_list):
        file_size = (
            os.path.getsize(file_path) if os.path.exists(file_path) else 0
        )
        logger.info(
            "    → %s: %s (%s)", 
            target, 
            os.path.basename(file_path), 
            format_file_size(file_size)
        )


def log_transfer_summary(transfer_files: dict, transfers_base_dir: str) -> None:
    """Log summary of generated transfer files."""
    logger.info("Generated %s transfer files:", len(transfer_files))
    files_by_source = group_files_by_source(transfer_files)
    for source in sorted(files_by_source.keys()):
        log_source_files(source, files_by_source[source])
    logger.info("\nTransfer files saved to: %s", transfers_base_dir)


def log_and_generate(
    analytics_dir: str, 
    transfers_base_dir: str, 
    has_date_header: bool, 
    first_line: str
) -> dict:
    """Log info and generate transfer files."""
    logger.info("Generating transfer files...")
    logger.info("-" * 50)
    logger.info("Using latest analytics files for each target branch...")
    return generate_transfer_files(
        analytics_dir, transfers_base_dir, has_date_header, first_line
    )


def execute_transfer_generation(
    analytics_dir: str, 
    transfers_base_dir: str, 
    analytics_files: dict
) -> bool:
    """Execute the transfer generation process."""
    has_date_header, first_line = finders.extract_date_header_info(
        analytics_dir, analytics_files
    )
    transfer_files = log_and_generate(
        analytics_dir, transfers_base_dir, has_date_header, first_line
    )
    
    if not transfer_files:
        logger.warning("No transfers found between branches")
        return False
    
    log_transfer_summary(transfer_files, transfers_base_dir)
    return True


def run_transfer_generation(
    analytics_dir: str, 
    transfers_base_dir: str, 
    analytics_files: dict
) -> bool:
    """Run transfer generation with error handling."""
    try:
        return execute_transfer_generation(
            analytics_dir, transfers_base_dir, analytics_files
        )
    except ValueError as error:
        logger.error("Error: %s", error)
        return False
    except Exception as error:
        logger.exception("Error during transfer generation: %s", error)
        return False
