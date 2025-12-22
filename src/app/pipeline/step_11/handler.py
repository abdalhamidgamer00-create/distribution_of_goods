"""
Step 11: Generate combined transfer files

Main handler that combines regular transfers with remaining surplus (directed to admin).
Provides two output modes: merged (all targets in one file) and separate (per target branch).
"""

import os
from src.core.domain.branches.config import get_branches
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_11.file_combiner import (
    combine_transfers_and_surplus,
    generate_merged_files,
    generate_separate_files,
    get_timestamp,
)
from src.app.pipeline.step_11.excel_formatter import (
    convert_to_excel_with_formatting,
)

logger = get_logger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

TRANSFERS_DIR = os.path.join("data", "output", "transfers", "csv")
REMAINING_SURPLUS_DIR = os.path.join("data", "output", "remaining_surplus", "csv")
ANALYTICS_DIR = os.path.join("data", "output", "branches", "analytics")

OUTPUT_MERGED_CSV = os.path.join("data", "output", "combined_transfers", "merged", "csv")
OUTPUT_MERGED_EXCEL = os.path.join("data", "output", "combined_transfers", "merged", "excel")
OUTPUT_SEPARATE_CSV = os.path.join("data", "output", "combined_transfers", "separate", "csv")
OUTPUT_SEPARATE_EXCEL = os.path.join("data", "output", "combined_transfers", "separate", "excel")


# =============================================================================
# PUBLIC API
# =============================================================================

def step_11_generate_combined_transfers(use_latest_file: bool = None) -> bool:
    """Step 11: Generate combined transfer files with remaining surplus."""
    if not _validate_input_directories():
        return False
    _create_output_directories()
    try:
        total_merged, total_separate = _process_all_branches(get_timestamp())
        _log_summary(total_merged, total_separate)
        return total_merged > 0 or total_separate > 0
    except Exception as error:
        logger.exception(f"Error generating combined transfer files: {error}")
        return False


# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def _validate_input_directories() -> bool:
    """Validate that required input directories exist."""
    if not os.path.exists(TRANSFERS_DIR):
        logger.error(f"Transfers directory not found: {TRANSFERS_DIR}\nPlease run Step 7 (Generate Transfer Files) first")
        return False
    if not os.path.exists(REMAINING_SURPLUS_DIR):
        logger.error(f"Remaining surplus directory not found: {REMAINING_SURPLUS_DIR}\nPlease run Step 9 (Generate Remaining Surplus) first")
        return False
    return True


def _create_output_directories() -> None:
    """Create output directories if they don't exist."""
    for directory_path in [OUTPUT_MERGED_CSV, OUTPUT_MERGED_EXCEL, 
                           OUTPUT_SEPARATE_CSV, OUTPUT_SEPARATE_EXCEL]:
        os.makedirs(directory_path, exist_ok=True)


# =============================================================================
# DATA RETRIEVAL HELPERS
# =============================================================================

def _get_combined_data(branch: str):
    """Get combined data for a branch."""
    return combine_transfers_and_surplus(
        branch=branch, transfers_dir=TRANSFERS_DIR,
        surplus_dir=REMAINING_SURPLUS_DIR, analytics_dir=ANALYTICS_DIR,
    )


# =============================================================================
# FILE GENERATION HELPERS
# =============================================================================

def _convert_and_count(files: list, excel_output_dir: str) -> int:
    """Convert files to Excel and return count."""
    if files:
        convert_to_excel_with_formatting(csv_files=files, excel_output_dir=excel_output_dir)
        return len(files)
    return 0


def _generate_merged_output(combined_data, branch: str, timestamp: str) -> int:
    """Generate merged files (all targets in one file) and convert to Excel."""
    merged_files = generate_merged_files(df=combined_data, branch=branch, csv_output_dir=OUTPUT_MERGED_CSV, timestamp=timestamp)
    return _convert_and_count(merged_files, OUTPUT_MERGED_EXCEL)


def _generate_separate_output(combined_data, branch: str, timestamp: str) -> int:
    """Generate separate files (per target branch) and convert to Excel."""
    separate_files = generate_separate_files(df=combined_data, branch=branch, csv_output_dir=OUTPUT_SEPARATE_CSV, timestamp=timestamp)
    return _convert_and_count(separate_files, OUTPUT_SEPARATE_EXCEL)


# =============================================================================
# BRANCH PROCESSING HELPERS
# =============================================================================

def _process_single_branch(branch: str, timestamp: str) -> tuple:
    """Process a single branch and return (merged_count, separate_count)."""
    logger.info(f"Processing branch: {branch}")
    combined_data = _get_combined_data(branch)
    
    if combined_data is None or combined_data.empty:
        logger.warning(f"No data to combine for branch: {branch}")
        return 0, 0
    
    return _generate_merged_output(combined_data, branch, timestamp), _generate_separate_output(combined_data, branch, timestamp)


def _process_all_branches(timestamp: str) -> tuple:
    """Process all branches and return total counts."""
    total_merged = 0
    total_separate = 0
    for branch in get_branches():
        merged, separate = _process_single_branch(branch, timestamp)
        total_merged += merged
        total_separate += separate
    return total_merged, total_separate


# =============================================================================
# LOGGING HELPERS
# =============================================================================

def _log_summary(total_merged: int, total_separate: int) -> None:
    """Log summary of generated files."""
    logger.info("=" * 50 + f"\nGenerated {total_merged} merged files (CSV + Excel)\nGenerated {total_separate} separate files (CSV + Excel)\nMerged output: {OUTPUT_MERGED_EXCEL}\nSeparate output: {OUTPUT_SEPARATE_EXCEL}")
