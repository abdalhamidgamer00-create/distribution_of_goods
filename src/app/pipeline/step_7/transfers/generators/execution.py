"""Execution logic for transfer generation."""

import os
from src.shared.utils.logging_utils import get_logger
from src.services.transfers.generators.transfer_generator import generate_transfer_files
from src.app.pipeline.step_7.transfers import finders
from src.app.pipeline.step_7.transfers.generators.logging import log_transfer_summary

logger = get_logger(__name__)


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
