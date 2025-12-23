"""File I/O helpers."""

import os
import pandas as pd
from src.shared.dataframes.validators import ensure_columns
from src.core.domain.classification.product_classifier import (
    classify_product_type,
)


def write_csv_to_file(
    dataframe: pd.DataFrame, 
    filepath: str, 
    has_date_header: bool, 
    first_line: str
) -> None:
    """Write DataFrame to CSV with optional date header."""
    with open(filepath, 'w', encoding='utf-8-sig', newline='') as file_handle:
        if has_date_header:
            file_handle.write(first_line + '\n')
        dataframe.to_csv(file_handle, index=False, lineterminator='\n')


def save_category_file(
    category_df: pd.DataFrame, 
    file_folder: str, 
    base_folder_name: str,
    category: str, 
    timestamp: str, 
    has_date_header: bool, 
    first_line: str
) -> str:
    """Save a category DataFrame to CSV file."""
    category_df = category_df.drop('product_type', axis=1)
    category_df = category_df.sort_values(
        'product_name', ascending=True, key=lambda column: column.str.lower()
    )
    
    category_file = f"{base_folder_name}_{timestamp}_{category}.csv"
    category_path = os.path.join(file_folder, category_file)
    
    write_csv_to_file(
        category_df, category_path, has_date_header, first_line
    )
    return category_path


def prepare_transfer_dataframe(transfer_file_path: str) -> pd.DataFrame:
    """Load and prepare transfer DataFrame with product types."""
    dataframe = pd.read_csv(transfer_file_path, encoding='utf-8-sig')
    ensure_columns(
        dataframe, 
        ["code", "product_name", "quantity_to_transfer"], 
        context=f"transfer file {transfer_file_path}"
    )
    dataframe['product_type'] = dataframe['product_name'].apply(
        classify_product_type
    )
    return dataframe
