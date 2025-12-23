"""Separate files generation logic."""

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


def generate_separate_files(
    df: pd.DataFrame, 
    branch: str, 
    csv_output_dir: str, 
    timestamp: str = None
) -> List[Dict]:
    """Generate separate files (one per target branch per product type)."""
    if df is None or df.empty:
        return []
    
    timestamp = timestamp or get_timestamp()
    if 'product_type' not in df.columns:
        df = add_product_type_column(df)
    
    files_info = []
    dirname = f"transfers_from_{branch}_{timestamp}"
    source_dir = os.path.join(csv_output_dir, dirname)
    
    for target in df['target_branch'].unique():
        target_output_dir = os.path.join(source_dir, f"to_{target}")
        os.makedirs(target_output_dir, exist_ok=True)
        
        target_df = df[df['target_branch'] == target]
        
        for p_type in PRODUCT_TYPES:
            type_df = target_df[target_df['product_type'] == p_type]
            if type_df.empty:
                continue
                
            output_df = prepare_and_sort(type_df)
            name = (
                f"transfer_from_{branch}_to_{target}_"
                f"{p_type}_{timestamp}.csv"
            )
            filepath = os.path.join(target_output_dir, name)
            
            output_df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            files_info.append({
                'path': filepath, 
                'product_type': p_type, 
                'target': target, 
                'count': len(output_df)
            })
            
    return files_info
