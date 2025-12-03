"""Split transfer files by product type"""

import os
from datetime import datetime
import pandas as pd

from src.core.domain.classification.product_classifier import (
    classify_product_type,
    get_product_categories,
)
from src.shared.dataframes.validators import ensure_columns
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def split_transfer_file_by_type(transfer_file_path: str, output_dir: str, has_date_header: bool = False, first_line: str = "") -> dict:
    """
    Split a transfer CSV file into multiple files by product type
    
    Each file's split files are saved in a dedicated subfolder
    
    Args:
        transfer_file_path: Path to input transfer CSV file
        output_dir: Directory to save split files
        has_date_header: Whether to include date header in output files
        first_line: First line (date header) to write if has_date_header is True
        
    Returns:
        Dictionary mapping product type to output file path
    """
    try:
        df = pd.read_csv(transfer_file_path, encoding='utf-8-sig')
        ensure_columns(
            df,
            ["code", "product_name", "quantity_to_transfer"],
            context=f"transfer file {transfer_file_path}",
        )
        
        df['product_type'] = df['product_name'].apply(classify_product_type)
        
        categories = get_product_categories()
        output_files = {}
        
        base_name = os.path.splitext(os.path.basename(transfer_file_path))[0]
        
        # Get base folder name (the parent directory name)
        base_folder_name = os.path.basename(os.path.dirname(transfer_file_path))
        
        # Extract target branch name from file name (e.g., "from_admin_to_wardani" -> "wardani")
        target_branch = None
        if '_to_' in base_name:
            parts = base_name.split('_to_')
            if len(parts) > 1:
                target_branch = parts[-1]  # Get the last part after "_to_"
        
        # Replace "other_branches" with target branch name in base_folder_name
        if target_branch:
            base_folder_name = base_folder_name.replace('_to_other_branches', f'_to_{target_branch}')
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create a dedicated folder for this file's split files
        file_folder = os.path.join(output_dir, base_name)
        os.makedirs(file_folder, exist_ok=True)
        
        for category in categories:
            category_df = df[df['product_type'] == category].copy()
            
            if len(category_df) > 0:
                category_df = category_df.drop('product_type', axis=1)
                category_df = category_df.sort_values(
                    'product_name', 
                    ascending=True,
                    key=lambda x: x.str.lower()
                )
                
                # Full filename with base folder name, timestamp, and category
                category_file = f"{base_folder_name}_{timestamp}_{category}.csv"
                category_path = os.path.join(file_folder, category_file)
                
                with open(category_path, 'w', encoding='utf-8-sig', newline='') as f:
                    if has_date_header:
                        f.write(first_line + '\n')
                    category_df.to_csv(f, index=False, lineterminator='\n')
                
                output_files[category] = category_path
        
        return output_files
    
    except Exception as e:
        logger.exception("Error splitting file %s: %s", transfer_file_path, e)
        return {}


def split_all_transfer_files(transfers_base_dir: str, has_date_header: bool = False, first_line: str = "") -> dict:
    """
    Split all transfer files by product type
    
    Args:
        transfers_base_dir: Base directory containing transfer files
        has_date_header: Whether to include date header in output files
        first_line: First line (date header) to write if has_date_header is True
        
    Returns:
        Dictionary mapping (source_branch, target_branch, category) to output file path
    """
    all_output_files = {}
    categories = get_product_categories()
    
    for root, dirs, files in os.walk(transfers_base_dir):
        for file in files:
            if file.endswith('.csv'):
                # Skip files that are already split (category files with timestamp pattern or old naming)
                is_split_file = any(file.endswith(f'_{cat}.csv') for cat in categories) or any(file == f'{cat}.csv' for cat in categories)
                if not is_split_file:
                    transfer_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(transfer_file_path, transfers_base_dir)
                    output_dir = os.path.dirname(os.path.join(transfers_base_dir, relative_path))
                    
                    split_files = split_transfer_file_by_type(transfer_file_path, output_dir, has_date_header, first_line)
                    
                    # Use base filename (without extension) to make key unique for each transfer file
                    base_filename = os.path.splitext(os.path.basename(transfer_file_path))[0]
                    
                    for category, file_path in split_files.items():
                        source_target = os.path.basename(os.path.dirname(transfer_file_path))
                        key = (source_target, base_filename, category)
                        all_output_files[key] = file_path
    
    return all_output_files

