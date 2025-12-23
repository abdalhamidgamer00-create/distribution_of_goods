"""Logging logic for Step 6."""

import os
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def log_timing_info(timing_stats: dict, total_duration: float, branch_count: int) -> None:
    """Log timing statistics."""
    if timing_stats:
        logger.info("Step 6 timing (seconds): prep=%.2f allocation=%.2f surplus=%.2f writes=%.2f total=%.2f",
                   timing_stats.get("prep_time", 0.0), timing_stats.get("allocation_time", 0.0),
                   timing_stats.get("surplus_time", 0.0), timing_stats.get("write_time", 0.0), total_duration)
        logger.info("Step 6 workload: products=%s branches=%s", timing_stats.get("num_products"), branch_count)


def log_split_results(output_files: dict, timing_stats: dict, total_duration: float,
                       branches_dir: str, analytics_dir: str) -> None:
    """Log split operation results."""
    logger.info("File split successfully into %s branch files:", len(output_files))
    for branch, file_path in output_files.items():
        logger.info("  - %s: %s", branch, os.path.basename(file_path))
    
    logger.info("Branch files saved to: %s", branches_dir)
    logger.info("Analytics files saved to: %s", analytics_dir)
    log_timing_info(timing_stats, total_duration, len(output_files))
