"""Logging helpers."""

import os
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_7.transfers.generators.formatting import (
    format_file_size
)
from src.app.pipeline.step_7.transfers.generators.grouping import (
    group_files_by_source
)

logger = get_logger(__name__)


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
