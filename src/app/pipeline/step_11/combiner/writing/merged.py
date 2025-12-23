"""Merged files generation logic."""

import os
import pandas as pd
from typing import List, Dict
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_11.combiner.constants import PRODUCT_TYPES
from src.app.pipeline.step_11.combiner.classifiers import (
    add_product_type_column
)
from src.app.pipeline.step_11.combiner.writing.utils import (
    get_timestamp, prepare_and_sort
)

logger = get_logger(__name__)


def generate_merged_files(
    df: pd.DataFrame, 
    branch: str, 
    csv_output_dir: str, 
    timestamp: str = None
) -> List[Dict]:
    """Generate merged files (all targets in one file per product type)."""
    if df is None or df.empty:
        return []
    
    timestamp = timestamp or get_timestamp()
    dirname = f"combined_transfers_from_{branch}_{timestamp}"
    branch_output_dir = os.path.join(csv_output_dir, dirname)
    os.makedirs(branch_output_dir, exist_ok=True)
    
    if 'product_type' not in df.columns:
        df = add_product_type_column(df)
        
    files_info = []
    for p_type in PRODUCT_TYPES:
        filename = f"{branch}_combined_{p_type}.csv"
        filepath = os.path.join(branch_output_dir, filename)
        
        type_df = df[df['product_type'] == p_type]
        if type_df.empty:
            continue
            
        output_df = prepare_and_sort(type_df)
        output_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        files_info.append({
            'path': filepath, 
            'product_type': p_type, 
            'count': len(output_df)
        })
        msg = f"Generated merged: {filename} ({len(output_df)} products)"
        logger.debug(msg)
        
    return files_info
