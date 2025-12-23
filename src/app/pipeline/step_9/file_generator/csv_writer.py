"""CSV writer logic."""

import os
import pandas as pd
from src.core.domain.classification.product_classifier import get_product_categories
from src.app.pipeline.step_9.file_generator.processing import process_category_dataframe


def generate_csv_files(
    dataframe: pd.DataFrame, 
    branch: str, 
    output_dir: str, 
    base_name: str,
    timestamp: str, 
    has_date_header: bool = False, 
    first_line: str = ''
) -> dict:
    """Generate CSV files split by product category."""
    branch_dir = os.path.join(output_dir, branch)
    os.makedirs(branch_dir, exist_ok=True)
    generated_files = {}
    for category in get_product_categories():
        category_dataframe = process_category_dataframe(dataframe, category)
        if category_dataframe is not None:
            generated_files[category] = _save_category_file(
                category_dataframe, branch_dir, base_name, branch, 
                timestamp, category, has_date_header, first_line
            )
    return generated_files


def _save_category_file(
    category_dataframe: pd.DataFrame, 
    branch_dir: str, 
    base_name: str, 
    branch: str, 
    timestamp: str, 
    category: str, 
    has_date_header: bool, 
    first_line: str
) -> dict:
    """Save category DataFrame and return file info."""
    filename = f"{base_name}_{branch}_remaining_surplus_{timestamp}_{category}.csv"
    file_path = os.path.join(branch_dir, filename)
    _write_category_csv(category_dataframe, file_path, has_date_header, first_line)
    return {
        'csv_path': file_path, 
        'df': category_dataframe, 
        'has_date_header': has_date_header, 
        'first_line': first_line
    }


def _write_category_csv(
    category_dataframe: pd.DataFrame, 
    file_path: str, 
    has_date_header: bool, 
    first_line: str
) -> None:
    """Write category DataFrame to CSV file."""
    with open(file_path, 'w', encoding='utf-8-sig', newline='') as file_handle:
        if has_date_header:
            file_handle.write(first_line + '\n')
        category_dataframe.to_csv(file_handle, index=False, lineterminator='\n')
