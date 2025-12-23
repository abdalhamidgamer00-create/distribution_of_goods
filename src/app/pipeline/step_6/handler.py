"""Step 6: Split CSV by branches handler"""

import os
import re
from datetime import datetime
from time import perf_counter
from src.shared.utils.file_handler import (
    get_file_path,
    get_csv_files,
    ensure_directory_exists,
)
from src.services.splitting.core import split_csv_by_branches
from src.core.domain.branches.config import get_branches
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.utils.file_selector import select_csv_file

logger = get_logger(__name__)


# =============================================================================
# PUBLIC API
# =============================================================================

def step_6_split_by_branches(use_latest_file: bool = None) -> bool:
    """Step 6: Split CSV file by branches."""
    renamed_dir = os.path.join("data", "output", "converted", "renamed")
    csv_files, branches_dir, analytics_dir = _setup_and_validate(renamed_dir)
    if csv_files is None:
        return False
    
    return _try_execute_split(renamed_dir, csv_files, branches_dir, analytics_dir, use_latest_file)


# =============================================================================
# SETUP HELPERS
# =============================================================================

def _ensure_branch_directories(branches: list, branches_dir: str, analytics_dir: str) -> None:
    """Ensure branch directories exist for all branches."""
    for branch in branches:
        ensure_directory_exists(os.path.join(branches_dir, branch))
        ensure_directory_exists(os.path.join(analytics_dir, branch))


def _setup_and_validate(renamed_dir: str) -> tuple:
    """Setup directories and validate input files."""
    csv_files = get_csv_files(renamed_dir)
    if not csv_files:
        logger.error("No CSV files found in %s", renamed_dir)
        return None, None, None
    return csv_files, os.path.join("data", "output", "branches", "files"), os.path.join("data", "output", "branches", "analytics")


def _generate_base_filename(csv_file: str) -> str:
    """Generate base filename with timestamp."""
    date_string = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name_only = os.path.basename(os.path.splitext(csv_file)[0])
    base_name_only = re.sub(r'_renamed|_\d{8}_\d{6}', '', base_name_only)
    return f"{base_name_only}_{date_string}"


# =============================================================================
# LOGGING HELPERS
# =============================================================================

def _log_timing_info(timing_stats: dict, total_duration: float, branch_count: int) -> None:
    """Log timing statistics."""
    if timing_stats:
        logger.info("Step 6 timing (seconds): prep=%.2f allocation=%.2f surplus=%.2f writes=%.2f total=%.2f",
                   timing_stats.get("prep_time", 0.0), timing_stats.get("allocation_time", 0.0),
                   timing_stats.get("surplus_time", 0.0), timing_stats.get("write_time", 0.0), total_duration)
        logger.info("Step 6 workload: products=%s branches=%s", timing_stats.get("num_products"), branch_count)


def _log_split_results(output_files: dict, timing_stats: dict, total_duration: float,
                       branches_dir: str, analytics_dir: str) -> None:
    """Log split operation results."""
    logger.info("File split successfully into %s branch files:", len(output_files))
    for branch, file_path in output_files.items():
        logger.info("  - %s: %s", branch, os.path.basename(file_path))
    
    logger.info("Branch files saved to: %s", branches_dir)
    logger.info("Analytics files saved to: %s", analytics_dir)
    _log_timing_info(timing_stats, total_duration, len(output_files))


# =============================================================================
# SPLIT EXECUTION HELPERS
# =============================================================================

def _run_split_and_log(csv_path: str, branches_dir: str, base_filename: str, analytics_dir: str) -> None:
    """Run split and log results."""
    total_start = perf_counter()
    output_files, timing_stats = split_csv_by_branches(csv_path, branches_dir, base_filename, analytics_dir)
    total_duration = perf_counter() - total_start
    _log_split_results(output_files, timing_stats, total_duration, branches_dir, analytics_dir)


def _execute_split(csv_path: str, csv_file: str, branches_dir: str, analytics_dir: str) -> bool:
    """Execute the split operation."""
    branches = get_branches()
    _ensure_branch_directories(branches, branches_dir, analytics_dir)
    
    base_filename = _generate_base_filename(csv_file)
    logger.info("Splitting %s by branches...", csv_file)
    logger.info("-" * 50)
    
    _run_split_and_log(csv_path, branches_dir, base_filename, analytics_dir)
    return True


def _try_execute_split(renamed_dir: str, csv_files: list, branches_dir: str, analytics_dir: str, use_latest_file: bool) -> bool:
    """Try to execute split with error handling."""
    try:
        csv_file = select_csv_file(renamed_dir, csv_files, use_latest_file)
        return _execute_split(get_file_path(csv_file, renamed_dir), csv_file, branches_dir, analytics_dir)
    except ValueError as error:
        logger.error("Error: %s", error)
        return False
    except Exception as error:
        logger.exception("Error during splitting: %s", error)
        return False
