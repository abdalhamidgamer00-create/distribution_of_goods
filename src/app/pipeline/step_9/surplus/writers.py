"""File generation and writers for surplus data."""

import os
from src.shared.utils.logging_utils import get_logger
from src.shared.utils.file_handler import get_latest_file
from src.app.pipeline.step_9.file_generator import (
    generate_csv_files,
    generate_excel_files,
    get_timestamp,
    extract_base_name,
)

logger = get_logger(__name__)


def create_csv_and_log(
    result_dataframe, 
    branch: str, 
    output_dir: str, 
    base_name: str, 
    timestamp: str, 
    has_date_header: bool, 
    first_line: str
) -> dict:
    """Create CSV files and log results."""
    csv_files = generate_csv_files(
        dataframe=result_dataframe, 
        branch=branch, 
        output_dir=output_dir, 
        base_name=base_name,
        timestamp=timestamp, 
        has_date_header=has_date_header, 
        first_line=first_line
    )
    
    if csv_files:
        logger.info(
            "Generated surplus files for %s: %d products in %d categories",
            branch, len(result_dataframe), len(csv_files)
        )
        return {'files': csv_files, 'total_products': len(result_dataframe)}
    return None


def generate_branch_files(
    result_dataframe, 
    branch: str, 
    has_date_header: bool, 
    first_line: str,
    analytics_dir: str,
    csv_output_dir: str
) -> dict:
    """Generate CSV files for branch surplus."""
    latest_file = get_latest_file(os.path.join(analytics_dir, branch), '.csv')
    base_name = extract_base_name(latest_file, branch)
    timestamp = get_timestamp()
    
    return create_csv_and_log(
        result_dataframe, 
        branch, 
        csv_output_dir, 
        base_name, 
        timestamp, 
        has_date_header, 
        first_line
    )


def convert_all_to_excel(all_branch_files: dict, output_dir: str) -> None:
    """Convert all CSV files to Excel format."""
    logger.info("Converting remaining surplus files to Excel format...")
    
    for branch, branch_info in all_branch_files.items():
        generate_excel_files(
            files_info=branch_info['files'],
            branch=branch,
            output_dir=output_dir
        )


def log_summary(all_branch_files: dict, csv_dir: str, excel_dir: str) -> None:
    """Log summary of generated files."""
    total_csv = sum(len(info['files']) for info in all_branch_files.values())
    total_excel = total_csv  # Same count for Excel
    
    logger.info("=" * 50)
    logger.info("Generated %d remaining surplus CSV files", total_csv)
    logger.info("Generated %d remaining surplus Excel files", total_excel)
    logger.info("CSV files saved to: %s (organized by branch)", csv_dir)
    logger.info("Excel files saved to: %s (organized by branch)", excel_dir)
