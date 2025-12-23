"""Execution logic for Step 6."""

import os
import re
from datetime import datetime
from time import perf_counter
from src.shared.utils.logging_utils import get_logger
from src.shared.utils.file_handler import get_file_path
from src.app.pipeline.utils.file_selector import select_csv_file
from src.core.domain.branches.config import get_branches
from src.services.splitting.core import split_csv_by_branches
from src.app.pipeline.step_6.splitter.setup import (
    ensure_branch_directories, 
)
from src.app.pipeline.step_6.splitter.logging_utils import log_split_results

logger = get_logger(__name__)


def generate_base_filename(csv_file: str) -> str:
    """Generate base filename with timestamp."""
    date_string = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name_only = os.path.basename(os.path.splitext(csv_file)[0])
    base_name_only = re.sub(r'_renamed|_\d{8}_\d{6}', '', base_name_only)
    return f"{base_name_only}_{date_string}"


def run_split_and_log(
    csv_path: str, branches_dir: str, base_filename: str, analytics_dir: str
) -> None:
    """Run split and log results."""
    total_start = perf_counter()
    res = split_csv_by_branches(
        csv_path, branches_dir, base_filename, analytics_dir
    )
    output_files, timing_stats = res
    total_duration = perf_counter() - total_start
    log_split_results(
        output_files, timing_stats, total_duration, 
        branches_dir, analytics_dir
    )


def execute_split(
    csv_path: str, csv_file: str, branches_dir: str, analytics_dir: str
) -> bool:
    """Execute the split operation."""
    branches = get_branches()
    ensure_branch_directories(branches, branches_dir, analytics_dir)
    
    base_filename = generate_base_filename(csv_file)
    logger.info("Splitting %s by branches...", csv_file)
    logger.info("-" * 50)
    
    run_split_and_log(csv_path, branches_dir, base_filename, analytics_dir)
    return True


def try_execute_split(
    renamed_dir: str, 
    csv_files: list, 
    branches_dir: str, 
    analytics_dir: str, 
    use_latest: bool
) -> bool:
    """Try to execute split with error handling."""
    try:
        csv_file = select_csv_file(renamed_dir, csv_files, use_latest)
        input_path = get_file_path(csv_file, renamed_dir)
        return execute_split(
            input_path, csv_file, branches_dir, analytics_dir
        )
    except ValueError as error:
        logger.error("Error: %s", error)
        return False
    except Exception as error:
        logger.exception("Error during splitting: %s", error)
        return False
