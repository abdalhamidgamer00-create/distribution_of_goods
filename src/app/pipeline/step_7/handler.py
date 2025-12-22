"""Step 7: Generate transfer files handler"""

import os
import re
from datetime import datetime
from src.shared.utils.file_handler import (
    get_csv_files,
    get_latest_file,
    get_file_path,
    ensure_directory_exists,
)
from src.core.domain.branches.config import get_branches
from src.services.transfers.generators.transfer_generator import generate_transfer_files
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _validate_analytics_directories(analytics_dir: str, branches: list) -> bool:
    """Validate that analytics directories exist for all branches."""
    for branch in branches:
        branch_dir = os.path.join(analytics_dir, branch)
        if not os.path.exists(branch_dir):
            logger.error("Analytics directory not found: %s", branch_dir)
            logger.error("Please run step 5 (Split by Branches) first to generate analytics files")
            return False
    return True


def _get_analytics_files(analytics_dir: str, branches: list) -> dict:
    """Get analytics files for all branches."""
    analytics_files = {}
    for branch in branches:
        branch_files = get_csv_files(os.path.join(analytics_dir, branch))
        if branch_files:
            analytics_files[branch] = branch_files
    return analytics_files


def _extract_date_header_info(analytics_dir: str, analytics_files: dict) -> tuple:
    """Extract date header information from first analytics file."""
    try:
        first_branch = list(analytics_files.keys())[0]
        latest_file = get_latest_file(os.path.join(analytics_dir, first_branch), '.csv')
        if latest_file:
            sample_path = os.path.join(analytics_dir, first_branch, latest_file)
            with open(sample_path, 'r', encoding='utf-8-sig') as f:
                first_line = f.readline().strip()
                from src.core.validation.data_validator import extract_dates_from_header
                start_date, end_date = extract_dates_from_header(first_line)
                if start_date and end_date:
                    return True, first_line
    except Exception:
        pass
    return False, ""


def _group_files_by_source(transfer_files: dict) -> dict:
    """Group transfer files by source branch."""
    files_by_source = {}
    for (source, target), file_path in transfer_files.items():
        if source not in files_by_source:
            files_by_source[source] = []
        files_by_source[source].append((target, file_path))
    return files_by_source


def _log_source_files(source: str, files_list: list) -> None:
    """Log files for a single source branch."""
    logger.info("\n  From %s (%d files):", source, len(files_list))
    for target, file_path in sorted(files_list):
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        logger.info("    → %s: %s (%s)", target, os.path.basename(file_path), _format_file_size(file_size))


def _log_transfer_summary(transfer_files: dict, transfers_base_dir: str) -> None:
    """Log summary of generated transfer files."""
    logger.info("Generated %s transfer files:", len(transfer_files))
    files_by_source = _group_files_by_source(transfer_files)
    for source in sorted(files_by_source.keys()):
        _log_source_files(source, files_by_source[source])
    logger.info("\nTransfer files saved to: %s", transfers_base_dir)


def _validate_and_get_files(analytics_dir: str, branches: list) -> dict:
    """Validate and get analytics files."""
    if not _validate_analytics_directories(analytics_dir, branches):
        return None
    
    analytics_files = _get_analytics_files(analytics_dir, branches)
    if not analytics_files:
        logger.error("No analytics files found in %s", analytics_dir)
        logger.error("Please run step 5 (Split by Branches) first to generate analytics files")
        return None
    return analytics_files


def _execute_transfer_generation(analytics_dir: str, transfers_base_dir: str, analytics_files: dict) -> bool:
    """Execute the transfer generation process."""
    has_date_header, first_line = _extract_date_header_info(analytics_dir, analytics_files)
    
    logger.info("Generating transfer files...")
    logger.info("-" * 50)
    logger.info("Using latest analytics files for each target branch...")
    
    transfer_files = generate_transfer_files(analytics_dir, transfers_base_dir, has_date_header, first_line)
    
    if not transfer_files:
        logger.warning("No transfers found between branches")
        return False
    
    _log_transfer_summary(transfer_files, transfers_base_dir)
    return True


def step_7_generate_transfers(use_latest_file: bool = None) -> bool:
    """Step 7: Generate transfer CSV files between branches."""
    analytics_dir = os.path.join("data", "output", "branches", "analytics")
    transfers_base_dir = os.path.join("data", "output", "transfers", "csv")
    branches = get_branches()
    
    analytics_files = _validate_and_get_files(analytics_dir, branches)
    if analytics_files is None:
        return False
    
    try:
        return _execute_transfer_generation(analytics_dir, transfers_base_dir, analytics_files)
    except ValueError as e:
        logger.error("Error: %s", e)
        return False
    except Exception as e:
        logger.exception("Error during transfer generation: %s", e)
        return False



def _format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

