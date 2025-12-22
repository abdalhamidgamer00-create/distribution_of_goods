"""Step 10: Generate shortage files handler

Generates files for products where total needed exceeds total surplus.
"""

import os
from datetime import datetime
import pandas as pd
from src.core.domain.branches.config import get_branches
from src.core.domain.classification.product_classifier import (
    classify_product_type,
    get_product_categories,
)
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_10.shortage_calculator import calculate_shortage_products

logger = get_logger(__name__)

# Output directories
ANALYTICS_DIR = os.path.join("data", "output", "branches", "analytics")
CSV_OUTPUT_DIR = os.path.join("data", "output", "shortage", "csv")
EXCEL_OUTPUT_DIR = os.path.join("data", "output", "shortage", "excel")


def _validate_analytics_directories(branches: list) -> bool:
    """Validate that analytics directories exist for all branches."""
    for branch in branches:
        branch_dir = os.path.join(ANALYTICS_DIR, branch)
        if not os.path.exists(branch_dir):
            logger.error("Analytics directory not found: %s", branch_dir)
            logger.error("Please run step 6 (Split by Branches) first")
            return False
    return True


def _write_csv_file(df: pd.DataFrame, csv_path: str, has_date_header: bool, first_line: str) -> None:
    """Write DataFrame to CSV file with optional date header."""
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
        if has_date_header:
            f.write(first_line + '\n')
        df.to_csv(f, index=False, lineterminator='\n')


def _process_single_category(shortage_df: pd.DataFrame, category: str, timestamp: str,
                              base_name: str, has_date_header: bool, first_line: str) -> dict:
    """Process a single category and return file info or None."""
    category_df = shortage_df[shortage_df['product_type'] == category].copy()
    if len(category_df) == 0:
        return None
    
    category_df = category_df.sort_values('shortage_quantity', ascending=False)
    category_df = category_df.drop('product_type', axis=1)
    
    csv_filename = f"{base_name}_{timestamp}_{category}.csv"
    csv_path = os.path.join(CSV_OUTPUT_DIR, csv_filename)
    _write_csv_file(category_df, csv_path, has_date_header, first_line)
    
    return {'csv_path': csv_path, 'df': category_df, 'count': len(category_df)}


def _generate_category_files(shortage_df: pd.DataFrame, categories: list, timestamp: str,
                             base_name: str, has_date_header: bool, first_line: str) -> dict:
    """Generate CSV files for each category."""
    generated_files = {}
    for category in categories:
        result = _process_single_category(shortage_df, category, timestamp, base_name, has_date_header, first_line)
        if result:
            generated_files[category] = result
    return generated_files


def _convert_all_to_excel(generated_files: dict) -> None:
    """Convert all generated CSV files to Excel."""
    logger.info("Converting to Excel format...")
    for category, file_info in generated_files.items():
        excel_filename = os.path.splitext(os.path.basename(file_info['csv_path']))[0] + '.xlsx'
        excel_path = os.path.join(EXCEL_OUTPUT_DIR, excel_filename)
        try:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                file_info['df'].to_excel(writer, index=False, sheet_name='Shortage Products')
        except Exception as e:
            logger.error("Error creating Excel file for %s: %s", category, e)


def _log_summary(generated_files: dict, categories: list, total_shortage: int) -> None:
    """Log generation summary."""
    logger.info("=" * 50)
    logger.info("Generated shortage files:")
    for category in categories:
        if category in generated_files:
            logger.info("  - %s: %d products", category, generated_files[category]['count'])
    logger.info("  - all (combined): %d products", generated_files['all']['count'])
    logger.info("")
    logger.info("Total shortage quantity: %d units", total_shortage)
    logger.info("")
    logger.info("CSV files saved to: %s", CSV_OUTPUT_DIR)
    logger.info("Excel files saved to: %s", EXCEL_OUTPUT_DIR)


def _prepare_shortage_data() -> tuple:
    """Prepare shortage data and classify products."""
    shortage_df, has_date_header, first_line = calculate_shortage_products(ANALYTICS_DIR)
    
    if shortage_df.empty:
        return None, None, None
    
    shortage_df['product_type'] = shortage_df['product_name'].apply(classify_product_type)
    return shortage_df, has_date_header, first_line


def _generate_all_files(shortage_df, has_date_header: bool, first_line: str) -> dict:
    """Generate category files and combined file."""
    os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)
    os.makedirs(EXCEL_OUTPUT_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = "shortage_products"
    categories = get_product_categories()
    
    generated_files = _generate_category_files(
        shortage_df, categories, timestamp, base_name, has_date_header, first_line
    )
    
    # Generate combined file
    all_df = shortage_df.drop('product_type', axis=1).copy()
    all_csv_path = os.path.join(CSV_OUTPUT_DIR, f"{base_name}_{timestamp}_all.csv")
    _write_csv_file(all_df, all_csv_path, has_date_header, first_line)
    generated_files['all'] = {'csv_path': all_csv_path, 'df': all_df, 'count': len(all_df)}
    
    return generated_files, categories


def _execute_shortage_generation(shortage_df, has_date_header: bool, first_line: str) -> bool:
    """Execute the shortage file generation process."""
    logger.info("Found %d products with shortage", len(shortage_df))
    
    generated_files, categories = _generate_all_files(shortage_df, has_date_header, first_line)
    _convert_all_to_excel(generated_files)
    _log_summary(generated_files, categories, int(shortage_df['shortage_quantity'].sum()))
    return True


def _run_shortage_generation() -> bool:
    """Run the shortage generation process."""
    logger.info("Calculating shortage products...")
    logger.info("-" * 50)
    
    shortage_df, has_date_header, first_line = _prepare_shortage_data()
    
    if shortage_df is None:
        logger.info("No shortage products found. All needs are covered by surplus!")
        return True
    
    return _execute_shortage_generation(shortage_df, has_date_header, first_line)


def step_10_generate_shortage_files(use_latest_file: bool = None) -> bool:
    """Step 10: Generate shortage files."""
    if not _validate_analytics_directories(get_branches()):
        return False
    
    try:
        return _run_shortage_generation()
    except Exception as e:
        logger.exception("Error generating shortage files: %s", e)
        return False


