"""File generator module

Generates CSV and Excel output files for remaining surplus.
"""

import os
from datetime import datetime
import pandas as pd
from src.core.domain.classification.product_classifier import (
    classify_product_type,
    get_product_categories,
)
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def add_product_type_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add product_type column based on product_name.
    
    Args:
        df: DataFrame with 'product_name' column
        
    Returns:
        DataFrame with added 'product_type' column
    """
    df = df.copy()
    df['product_type'] = df['product_name'].apply(classify_product_type)
    return df


def generate_csv_files(
    df: pd.DataFrame,
    branch: str,
    output_dir: str,
    base_name: str,
    timestamp: str,
    has_date_header: bool = False,
    first_line: str = ''
) -> dict:
    """
    Generate CSV files split by product category.
    
    Args:
        df: DataFrame with product data (must have 'product_type' column)
        branch: Branch name
        output_dir: Base output directory for CSV files
        base_name: Base name for output files
        timestamp: Timestamp string for file naming
        has_date_header: Whether to include date header
        first_line: Date header line content
        
    Returns:
        Dictionary mapping category -> file info dict
    """
    # Create branch directory
    branch_dir = os.path.join(output_dir, branch)
    os.makedirs(branch_dir, exist_ok=True)
    
    categories = get_product_categories()
    generated_files = {}
    
    for category in categories:
        category_df = df[df['product_type'] == category].copy()
        
        if len(category_df) == 0:
            continue
        
        # Sort by product_name (A to Z, case-insensitive)
        category_df = category_df.sort_values(
            'product_name', 
            ascending=True,
            key=lambda x: x.str.lower()
        )
        
        # Remove product_type column before saving
        category_df = category_df.drop('product_type', axis=1)
        
        # Generate filename and path
        filename = f"{base_name}_{branch}_remaining_surplus_{timestamp}_{category}.csv"
        file_path = os.path.join(branch_dir, filename)
        
        # Write CSV file
        with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
            if has_date_header:
                f.write(first_line + '\n')
            category_df.to_csv(f, index=False, lineterminator='\n')
        
        generated_files[category] = {
            'csv_path': file_path,
            'df': category_df,
            'has_date_header': has_date_header,
            'first_line': first_line
        }
    
    return generated_files


def generate_excel_files(files_info: dict, branch: str, output_dir: str) -> int:
    """
    Convert CSV files to Excel format.
    
    Args:
        files_info: Dictionary from generate_csv_files()
        branch: Branch name
        output_dir: Base output directory for Excel files
        
    Returns:
        Number of successfully created Excel files
    """
    # Create branch directory
    branch_dir = os.path.join(output_dir, branch)
    os.makedirs(branch_dir, exist_ok=True)
    
    success_count = 0
    
    for category, file_info in files_info.items():
        # Generate Excel filename
        csv_basename = os.path.basename(file_info['csv_path'])
        excel_filename = os.path.splitext(csv_basename)[0] + '.xlsx'
        excel_path = os.path.join(branch_dir, excel_filename)
        
        try:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                file_info['df'].to_excel(writer, index=False, sheet_name='Remaining Surplus')
            success_count += 1
        except Exception as e:
            logger.error("Error creating Excel file for %s/%s: %s", branch, category, e)
    
    return success_count


def get_timestamp() -> str:
    """Get current timestamp string for file naming."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def extract_base_name(filename: str, branch: str) -> str:
    """
    Extract base name from analytics filename.
    
    Args:
        filename: Analytics filename
        branch: Branch name to remove from filename
        
    Returns:
        Base name without branch suffix
    """
    base = os.path.splitext(filename)[0]
    return base.replace(f'_{branch}_analytics', '')

