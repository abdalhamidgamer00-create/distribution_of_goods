"""Output file generation writers."""
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from src.shared.utils.logging_utils import get_logger
from .constants import PRODUCT_TYPES
from .classifiers import add_product_type_column

logger = get_logger(__name__)

def get_timestamp() -> str:
    """Get current timestamp for filenames."""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def generate_merged_files(df: pd.DataFrame, branch: str, csv_output_dir: str, timestamp: str = None) -> List[Dict]:
    """Generate merged files (all targets in one file per product type)."""
    if df is None or df.empty:
        return []
    
    timestamp = timestamp or get_timestamp()
    branch_output_dir = os.path.join(csv_output_dir, f"combined_transfers_from_{branch}_{timestamp}")
    os.makedirs(branch_output_dir, exist_ok=True)
    
    if 'product_type' not in df.columns:
        df = add_product_type_column(df)
        
    files_info = []
    for product_type in PRODUCT_TYPES:
        filename = f"{branch}_combined_{product_type}.csv"
        filepath = os.path.join(branch_output_dir, filename)
        
        type_df = df[df['product_type'] == product_type]
        if type_df.empty:
            continue
            
        output_df = _prepare_and_sort(type_df)
        output_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        files_info.append({
            'path': filepath, 
            'product_type': product_type, 
            'count': len(output_df)
        })
        logger.debug(f"Generated merged: {filename} ({len(output_df)} products)")
        
    return files_info


def generate_separate_files(df: pd.DataFrame, branch: str, csv_output_dir: str, timestamp: str = None) -> List[Dict]:
    """Generate separate files (one file per target branch per product type)."""
    if df is None or df.empty:
        return []
    
    timestamp = timestamp or get_timestamp()
    if 'product_type' not in df.columns:
        df = add_product_type_column(df)
    
    files_info = []
    source_dir = os.path.join(csv_output_dir, f"transfers_from_{branch}_{timestamp}")
    
    for target in df['target_branch'].unique():
        target_output_dir = os.path.join(source_dir, f"to_{target}")
        os.makedirs(target_output_dir, exist_ok=True)
        
        target_df = df[df['target_branch'] == target]
        
        for product_type in PRODUCT_TYPES:
            type_df = target_df[target_df['product_type'] == product_type]
            if type_df.empty:
                continue
                
            output_df = _prepare_and_sort(type_df)
            filename = f"transfer_from_{branch}_to_{target}_{product_type}_{timestamp}.csv"
            filepath = os.path.join(target_output_dir, filename)
            
            output_df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            files_info.append({
                'path': filepath, 
                'product_type': product_type, 
                'target': target, 
                'count': len(output_df)
            })
            
    return files_info


def _prepare_and_sort(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare columns and sort DataFrame."""
    required_cols = ['code', 'product_name', 'quantity_to_transfer', 'target_branch', 
                     'transfer_type', 'sender_balance', 'receiver_balance']
    optional_cols = ['unit', 'selling_price', 'company']
    
    final_cols = [c for c in required_cols if c in df.columns]
    final_cols.extend(c for c in optional_cols if c in df.columns)
    
    out = df[final_cols].copy()
    if 'product_name' in out.columns:
        return out.sort_values('product_name', ascending=True, key=lambda x: x.str.lower())
    return out
