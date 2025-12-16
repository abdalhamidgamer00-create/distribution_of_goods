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

# Output directories
TRANSFERS_DIR = os.path.join("data", "output", "transfers", "csv")
REMAINING_SURPLUS_DIR = os.path.join("data", "output", "remaining_surplus", "csv")
ANALYTICS_DIR = os.path.join("data", "output", "branches", "analytics")

OUTPUT_MERGED_CSV = os.path.join("data", "output", "combined_transfers", "merged", "csv")
OUTPUT_MERGED_EXCEL = os.path.join("data", "output", "combined_transfers", "merged", "excel")
OUTPUT_SEPARATE_CSV = os.path.join("data", "output", "combined_transfers", "separate", "csv")
OUTPUT_SEPARATE_EXCEL = os.path.join("data", "output", "combined_transfers", "separate", "excel")


def step_11_generate_combined_transfers(use_latest_file: bool = None) -> bool:
    """
    Step 11: Generate combined transfer files with remaining surplus.
    
    Creates both merged and separate output modes:
    - Merged: All target branches in one file per product type
    - Separate: One file per target branch per product type
    
    Includes:
    - sender_balance: Balance of sending branch (colored)
    - receiver_balance: Balance of receiving branch (colored)
    - transfer_type: 'normal' or 'surplus'
    
    Args:
        use_latest_file: Not used, kept for consistency
        
    Returns:
        True if successful, False otherwise
    """
    branches = get_branches()
    
    # Validate input directories
    if not _validate_input_directories():
        return False
    
    # Create output directories
    _create_output_directories()
    
    # Generate shared timestamp for all files in this run
    timestamp = get_timestamp()
    
    try:
        total_merged = 0
        total_separate = 0
        
        # Process each branch
        # Note: admin sends transfers to other branches but doesn't have remaining surplus
        for branch in branches:
            logger.info(f"Processing branch: {branch}")
            
            # Combine transfers and surplus data
            combined_data = combine_transfers_and_surplus(
                branch=branch,
                transfers_dir=TRANSFERS_DIR,
                surplus_dir=REMAINING_SURPLUS_DIR,
                analytics_dir=ANALYTICS_DIR,
            )
            
            if combined_data is None or combined_data.empty:
                logger.warning(f"No data to combine for branch: {branch}")
                continue
            
            # Generate merged files (all targets in one file)
            merged_files = generate_merged_files(
                df=combined_data,
                branch=branch,
                csv_output_dir=OUTPUT_MERGED_CSV,
                timestamp=timestamp,
            )
            
            if merged_files:
                # Convert to Excel with conditional formatting
                convert_to_excel_with_formatting(
                    csv_files=merged_files,
                    excel_output_dir=OUTPUT_MERGED_EXCEL,
                )
                total_merged += len(merged_files)
            
            # Generate separate files (per target branch)
            separate_files = generate_separate_files(
                df=combined_data,
                branch=branch,
                csv_output_dir=OUTPUT_SEPARATE_CSV,
                timestamp=timestamp,
            )
            
            if separate_files:
                # Convert to Excel with conditional formatting
                convert_to_excel_with_formatting(
                    csv_files=separate_files,
                    excel_output_dir=OUTPUT_SEPARATE_EXCEL,
                )
                total_separate += len(separate_files)
        
        # Log summary
        _log_summary(total_merged, total_separate)
        
        return total_merged > 0 or total_separate > 0
        
    except Exception as e:
        logger.exception(f"Error generating combined transfer files: {e}")
        return False


def _validate_input_directories() -> bool:
    """Validate that required input directories exist."""
    if not os.path.exists(TRANSFERS_DIR):
        logger.error(f"Transfers directory not found: {TRANSFERS_DIR}")
        logger.error("Please run Step 7 (Generate Transfer Files) first")
        return False
    
    if not os.path.exists(REMAINING_SURPLUS_DIR):
        logger.error(f"Remaining surplus directory not found: {REMAINING_SURPLUS_DIR}")
        logger.error("Please run Step 9 (Generate Remaining Surplus) first")
        return False
    
    return True


def _create_output_directories() -> None:
    """Create output directories if they don't exist."""
    for dir_path in [OUTPUT_MERGED_CSV, OUTPUT_MERGED_EXCEL, 
                     OUTPUT_SEPARATE_CSV, OUTPUT_SEPARATE_EXCEL]:
        os.makedirs(dir_path, exist_ok=True)


def _log_summary(total_merged: int, total_separate: int) -> None:
    """Log summary of generated files."""
    logger.info("=" * 50)
    logger.info(f"Generated {total_merged} merged files (CSV + Excel)")
    logger.info(f"Generated {total_separate} separate files (CSV + Excel)")
    logger.info(f"Merged output: {OUTPUT_MERGED_EXCEL}")
    logger.info(f"Separate output: {OUTPUT_SEPARATE_EXCEL}")
