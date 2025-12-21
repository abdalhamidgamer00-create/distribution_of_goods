"""Step 9: Generate remaining surplus files handler

Main handler that orchestrates the remaining surplus file generation process.
"""

import os
from src.core.domain.branches.config import get_branches
from src.shared.utils.file_handler import get_latest_file
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_9.analytics_reader import (
    read_analytics_file,
    get_latest_analytics_path,
)
from src.app.pipeline.step_9.surplus_calculator import (
    calculate_total_withdrawals,
    calculate_remaining_surplus,
    validate_analytics_columns,
)
from src.app.pipeline.step_9.file_generator import (
    add_product_type_column,
    generate_csv_files,
    generate_excel_files,
    get_timestamp,
    extract_base_name,
)

logger = get_logger(__name__)

# Output directories
ANALYTICS_DIR = os.path.join("data", "output", "branches", "analytics")
CSV_OUTPUT_DIR = os.path.join("data", "output", "remaining_surplus", "csv")
EXCEL_OUTPUT_DIR = os.path.join("data", "output", "remaining_surplus", "excel")


def step_9_generate_remaining_surplus(use_latest_file: bool = None) -> bool:
    """
    Step 9: Generate remaining surplus files for each branch.
    
    Creates CSV and Excel files containing products with remaining surplus
    after distribution to all needing branches.
    
    Args:
        use_latest_file: Not used, kept for consistency with other handlers
        
    Returns:
        True if successful, False otherwise
    """
    branches = get_branches()
    
    # Validate analytics directories exist
    if not _validate_analytics_directories(branches):
        return False
    
    try:
        all_branch_files = {}
        
        # Process each branch
        for branch in branches:
            branch_files = _process_branch(branch)
            if branch_files:
                all_branch_files[branch] = branch_files
        
        if not all_branch_files:
            logger.warning("No remaining surplus files were created")
            return False
        
        # Convert to Excel
        _convert_all_to_excel(all_branch_files)
        
        # Log summary
        _log_summary(all_branch_files)
        
        return True
        
    except Exception as e:
        logger.exception("Error generating remaining surplus files: %s", e)
        return False


def _validate_analytics_directories(branches: list) -> bool:
    """Check that all branch analytics directories exist."""
    for branch in branches:
        branch_dir = os.path.join(ANALYTICS_DIR, branch)
        if not os.path.exists(branch_dir):
            logger.error("Analytics directory not found: %s", branch_dir)
            logger.error("Please run step 6 (Split by Branches) first")
            return False
    return True


def _load_and_validate_analytics(branch: str):
    """Load and validate analytics file for a branch."""
    analytics_path = get_latest_analytics_path(ANALYTICS_DIR, branch)
    if not analytics_path:
        logger.warning("No analytics file found for branch: %s", branch)
        return None, None, None
    
    df, has_date_header, first_line = read_analytics_file(analytics_path)
    if df is None:
        return None, None, None
    
    missing_cols = validate_analytics_columns(df)
    if missing_cols:
        logger.error("Missing required columns in %s: %s", analytics_path, missing_cols)
        return None, None, None
    
    return df, has_date_header, first_line


def _calculate_branch_surplus(df, branch: str):
    """Calculate remaining surplus for a branch."""
    total_withdrawals = calculate_total_withdrawals(ANALYTICS_DIR, branch)
    result_df = calculate_remaining_surplus(df, total_withdrawals)
    
    if result_df.empty:
        logger.info("No remaining surplus for branch: %s", branch)
        return None
    
    return add_product_type_column(result_df)


def _generate_branch_files(result_df, branch: str, has_date_header: bool, first_line: str) -> dict:
    """Generate CSV files for branch surplus."""
    latest_file = get_latest_file(os.path.join(ANALYTICS_DIR, branch), '.csv')
    base_name = extract_base_name(latest_file, branch)
    timestamp = get_timestamp()
    
    csv_files = generate_csv_files(
        df=result_df,
        branch=branch,
        output_dir=CSV_OUTPUT_DIR,
        base_name=base_name,
        timestamp=timestamp,
        has_date_header=has_date_header,
        first_line=first_line
    )
    
    if csv_files:
        logger.info("Generated remaining surplus files for %s: %d products in %d categories",
                   branch, len(result_df), len(csv_files))
        return {'files': csv_files, 'total_products': len(result_df)}
    
    return None


def _process_branch(branch: str) -> dict:
    """Process a single branch and generate its remaining surplus files."""
    df, has_date_header, first_line = _load_and_validate_analytics(branch)
    if df is None:
        return None
    
    result_df = _calculate_branch_surplus(df, branch)
    if result_df is None:
        return None
    
    return _generate_branch_files(result_df, branch, has_date_header, first_line)


def _convert_all_to_excel(all_branch_files: dict) -> None:
    """Convert all CSV files to Excel format."""
    logger.info("Converting remaining surplus files to Excel format...")
    
    for branch, branch_info in all_branch_files.items():
        generate_excel_files(
            files_info=branch_info['files'],
            branch=branch,
            output_dir=EXCEL_OUTPUT_DIR
        )


def _log_summary(all_branch_files: dict) -> None:
    """Log summary of generated files."""
    total_csv = sum(len(info['files']) for info in all_branch_files.values())
    total_excel = total_csv  # Same count for Excel
    
    logger.info("=" * 50)
    logger.info("Generated %d remaining surplus CSV files", total_csv)
    logger.info("Generated %d remaining surplus Excel files", total_excel)
    logger.info("CSV files saved to: %s (organized by branch)", CSV_OUTPUT_DIR)
    logger.info("Excel files saved to: %s (organized by branch)", EXCEL_OUTPUT_DIR)

