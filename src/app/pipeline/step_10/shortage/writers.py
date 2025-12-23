"""File generation and summary logging for shortage generation."""

import os
import pandas as pd
from datetime import datetime
from src.shared.utils.logging_utils import get_logger
from src.core.domain.classification.product_classifier import (
    get_product_categories,
)
from src.app.pipeline.step_10.shortage import processing

logger = get_logger(__name__)


def write_csv_file(
    dataframe: pd.DataFrame, 
    csv_path: str, 
    has_date_header: bool, 
    first_line: str
) -> None:
    """Write DataFrame to CSV file with optional date header."""
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as file_handle:
        if has_date_header:
            file_handle.write(first_line + '\n')
        dataframe.to_csv(file_handle, index=False, lineterminator='\n')


def process_single_category(
    shortage_dataframe: pd.DataFrame, 
    category: str, 
    timestamp: str,
    base_name: str, 
    has_date_header: bool, 
    first_line: str,
    output_dir: str
) -> dict:
    """Process a single category and return file info or None."""
    category_dataframe = processing.prepare_category_dataframe(
        shortage_dataframe, category
    )
    if category_dataframe is None:
        return None
    
    csv_filename = f"{base_name}_{timestamp}_{category}.csv"
    csv_path = os.path.join(output_dir, csv_filename)
    write_csv_file(category_dataframe, csv_path, has_date_header, first_line)
    
    return {
        'csv_path': csv_path, 
        'df': category_dataframe, 
        'count': len(category_dataframe)
    }


def generate_category_files(
    shortage_dataframe: pd.DataFrame, 
    categories: list, 
    timestamp: str,
    base_name: str, 
    has_date_header: bool, 
    first_line: str,
    output_dir: str
) -> dict:
    """Generate CSV files for each category."""
    generated_files = {}
    for category in categories:
        result = process_single_category(
            shortage_dataframe, 
            category, 
            timestamp, 
            base_name, 
            has_date_header, 
            first_line,
            output_dir
        )
        if result:
            generated_files[category] = result
    return generated_files


def create_combined_file(
    shortage_dataframe, 
    timestamp: str, 
    base_name: str, 
    has_date_header: bool, 
    first_line: str,
    output_dir: str
) -> dict:
    """Create combined shortage file."""
    all_dataframe = shortage_dataframe.drop('product_type', axis=1).copy()
    all_csv_path = os.path.join(output_dir, f"{base_name}_{timestamp}_all.csv")
    write_csv_file(all_dataframe, all_csv_path, has_date_header, first_line)
    return {
        'csv_path': all_csv_path, 
        'df': all_dataframe, 
        'count': len(all_dataframe)
    }


def generate_all_files(
    shortage_dataframe, 
    has_date_header: bool, 
    first_line: str,
    csv_output_dir: str,
    excel_output_dir: str
) -> tuple:
    """Generate category files and combined file."""
    os.makedirs(csv_output_dir, exist_ok=True)
    os.makedirs(excel_output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = "shortage_products"
    categories = get_product_categories()
    
    generated_files = generate_category_files(
        shortage_dataframe, 
        categories, 
        timestamp, 
        base_name, 
        has_date_header, 
        first_line,
        csv_output_dir
    )
    
    generated_files['all'] = create_combined_file(
        shortage_dataframe, 
        timestamp, 
        base_name, 
        has_date_header, 
        first_line,
        csv_output_dir
    )
    
    return generated_files, categories


def convert_all_to_excel(generated_files: dict, output_dir: str) -> None:
    """Convert all generated CSV files to Excel."""
    logger.info("Converting to Excel format...")
    for category, file_info in generated_files.items():
        base_name = os.path.basename(file_info['csv_path'])
        excel_filename = os.path.splitext(base_name)[0] + '.xlsx'
        excel_path = os.path.join(output_dir, excel_filename)
        try:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                file_info['df'].to_excel(
                    writer, index=False, sheet_name='Shortage Products'
                )
        except Exception as error:
            logger.error("Error creating Excel file for %s: %s", category, error)


def log_summary(
    generated_files: dict, 
    categories: list, 
    total_shortage: int,
    csv_output_dir: str,
    excel_output_dir: str
) -> None:
    """Log generation summary."""
    logger.info("=" * 50 + "\nGenerated shortage files:")
    for category in categories:
        if category in generated_files:
            logger.info(
                "  - %s: %d products", category, generated_files[category]['count']
            )
            
    logger.info(
        "  - all (combined): %d products\n\n"
        "Total shortage quantity: %d units\n\n"
        "CSV files saved to: %s\nExcel files saved to: %s", 
        generated_files['all']['count'], 
        total_shortage, 
        csv_output_dir, 
        excel_output_dir
    )
