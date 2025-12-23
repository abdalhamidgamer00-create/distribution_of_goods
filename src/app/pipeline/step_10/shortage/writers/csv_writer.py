"""CSV writing logic for shortage files."""

import os
import pandas as pd
from src.app.pipeline.step_10.shortage import processing


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
