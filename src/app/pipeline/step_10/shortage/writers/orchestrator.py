"""Orchestrator for writing shortage files."""

import os
from datetime import datetime
from src.core.domain.classification.product_classifier import (
    get_product_categories,
)
from src.app.pipeline.step_10.shortage.writers import csv_writer


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
    
    generated_files = csv_writer.generate_category_files(
        shortage_dataframe, 
        categories, 
        timestamp, 
        base_name, 
        has_date_header, 
        first_line,
        csv_output_dir
    )
    
    generated_files['all'] = csv_writer.create_combined_file(
        shortage_dataframe, 
        timestamp, 
        base_name, 
        has_date_header, 
        first_line,
        csv_output_dir
    )
    
    return generated_files, categories
