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


# =============================================================================
# CONSTANTS
# =============================================================================

ANALYTICS_DIR = os.path.join("data", "output", "branches", "analytics")
CSV_OUTPUT_DIR = os.path.join("data", "output", "shortage", "csv")
EXCEL_OUTPUT_DIR = os.path.join("data", "output", "shortage", "excel")


# =============================================================================
# PUBLIC API
# =============================================================================

def step_10_generate_shortage_files(use_latest_file: bool = None) -> bool:
    """Step 10: Generate shortage files."""
    if not _validate_analytics_directories(get_branches()):
        return False
    
    try:
        return _run_shortage_generation()
    except Exception as error:
        logger.exception("Error generating shortage files: %s", error)
        return False


# =============================================================================
# VALIDATION HELPERS
# =============================================================================

def _validate_analytics_directories(branches: list) -> bool:
    """Validate that analytics directories exist for all branches."""
    for branch in branches:
        branch_dir = os.path.join(ANALYTICS_DIR, branch)
        if not os.path.exists(branch_dir):
            logger.error("Analytics directory not found: %s", branch_dir)
            logger.error("Please run step 6 (Split by Branches) first")
            return False
    return True


# =============================================================================
# DATA PREPARATION HELPERS
# =============================================================================

def _prepare_shortage_data() -> tuple:
    """Prepare shortage data and classify products."""
    shortage_dataframe, has_date_header, first_line = calculate_shortage_products(ANALYTICS_DIR)
    
    if shortage_dataframe.empty:
        return None, None, None
    
    shortage_dataframe['product_type'] = shortage_dataframe['product_name'].apply(classify_product_type)
    return shortage_dataframe, has_date_header, first_line


def _prepare_category_dataframe(shortage_dataframe: pd.DataFrame, category: str) -> pd.DataFrame:
    """Prepare category dataframe for output."""
    category_dataframe = shortage_dataframe[shortage_dataframe['product_type'] == category].copy()
    if len(category_dataframe) == 0:
        return None
    return category_dataframe.sort_values('shortage_quantity', ascending=False).drop('product_type', axis=1)


# =============================================================================
# FILE I/O HELPERS
# =============================================================================

def _write_csv_file(dataframe: pd.DataFrame, csv_path: str, has_date_header: bool, first_line: str) -> None:
    """Write DataFrame to CSV file with optional date header."""
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as file_handle:
        if has_date_header:
            file_handle.write(first_line + '\n')
        dataframe.to_csv(file_handle, index=False, lineterminator='\n')


# =============================================================================
# FILE GENERATION HELPERS
# =============================================================================

def _process_single_category(shortage_dataframe: pd.DataFrame, category: str, timestamp: str,
                              base_name: str, has_date_header: bool, first_line: str) -> dict:
    """Process a single category and return file info or None."""
    category_dataframe = _prepare_category_dataframe(shortage_dataframe, category)
    if category_dataframe is None:
        return None
    
    csv_filename = f"{base_name}_{timestamp}_{category}.csv"
    csv_path = os.path.join(CSV_OUTPUT_DIR, csv_filename)
    _write_csv_file(category_dataframe, csv_path, has_date_header, first_line)
    return {'csv_path': csv_path, 'df': category_dataframe, 'count': len(category_dataframe)}


def _generate_category_files(shortage_dataframe: pd.DataFrame, categories: list, timestamp: str,
                             base_name: str, has_date_header: bool, first_line: str) -> dict:
    """Generate CSV files for each category."""
    generated_files = {}
    for category in categories:
        result = _process_single_category(shortage_dataframe, category, timestamp, base_name, has_date_header, first_line)
        if result:
            generated_files[category] = result
    return generated_files


def _create_combined_file(shortage_dataframe, timestamp: str, base_name: str, 
                          has_date_header: bool, first_line: str) -> dict:
    """Create combined shortage file."""
    all_dataframe = shortage_dataframe.drop('product_type', axis=1).copy()
    all_csv_path = os.path.join(CSV_OUTPUT_DIR, f"{base_name}_{timestamp}_all.csv")
    _write_csv_file(all_dataframe, all_csv_path, has_date_header, first_line)
    return {'csv_path': all_csv_path, 'df': all_dataframe, 'count': len(all_dataframe)}


def _generate_all_files(shortage_dataframe, has_date_header: bool, first_line: str) -> dict:
    """Generate category files and combined file."""
    os.makedirs(CSV_OUTPUT_DIR, exist_ok=True)
    os.makedirs(EXCEL_OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = "shortage_products"
    categories = get_product_categories()
    generated_files = _generate_category_files(shortage_dataframe, categories, timestamp, base_name, has_date_header, first_line)
    generated_files['all'] = _create_combined_file(shortage_dataframe, timestamp, base_name, has_date_header, first_line)
    return generated_files, categories


# =============================================================================
# EXCEL CONVERSION HELPERS
# =============================================================================

def _convert_all_to_excel(generated_files: dict) -> None:
    """Convert all generated CSV files to Excel."""
    logger.info("Converting to Excel format...")
    for category, file_info in generated_files.items():
        excel_filename = os.path.splitext(os.path.basename(file_info['csv_path']))[0] + '.xlsx'
        excel_path = os.path.join(EXCEL_OUTPUT_DIR, excel_filename)
        try:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                file_info['df'].to_excel(writer, index=False, sheet_name='Shortage Products')
        except Exception as error:
            logger.error("Error creating Excel file for %s: %s", category, error)


# =============================================================================
# EXECUTION AND LOGGING HELPERS
# =============================================================================

def _run_shortage_generation() -> bool:
    """Run the shortage generation process."""
    logger.info("Calculating shortage products...\n" + "-" * 50)
    shortage_dataframe, has_date_header, first_line = _prepare_shortage_data()
    if shortage_dataframe is None:
        logger.info("No shortage products found. All needs are covered by surplus!")
        return True
    return _execute_shortage_generation(shortage_dataframe, has_date_header, first_line)


def _execute_shortage_generation(shortage_dataframe, has_date_header: bool, first_line: str) -> bool:
    """Execute the shortage file generation process."""
    logger.info("Found %d products with shortage", len(shortage_dataframe))
    
    generated_files, categories = _generate_all_files(shortage_dataframe, has_date_header, first_line)
    _convert_all_to_excel(generated_files)
    _log_summary(generated_files, categories, int(shortage_dataframe['shortage_quantity'].sum()))
    return True


def _log_summary(generated_files: dict, categories: list, total_shortage: int) -> None:
    """Log generation summary."""
    logger.info("=" * 50 + "\nGenerated shortage files:")
    for category in categories:
        if category in generated_files:
            logger.info("  - %s: %d products", category, generated_files[category]['count'])
    logger.info("  - all (combined): %d products\n\nTotal shortage quantity: %d units\n\nCSV files saved to: %s\nExcel files saved to: %s", 
                generated_files['all']['count'], total_shortage, CSV_OUTPUT_DIR, EXCEL_OUTPUT_DIR)
