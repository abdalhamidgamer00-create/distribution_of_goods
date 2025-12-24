"""Persistence logic for combined transfers (Step 11)."""

import os
import pandas as pd
from typing import List, Dict
from src.domain.models.entities import Branch
from src.infrastructure.persistence.excel_formatter import save_formatted_excel


def save_step11_combined_transfers(
    branch: Branch,
    merged_data: List[Dict], 
    separate_data: List[Dict],
    timestamp: str,
    base_dir: str = "data/output/combined_transfers"
) -> None:
    """Saves combined transfers (merged and separate) with clean structure."""
    _save_merged_outputs(branch, merged_data, timestamp, base_dir)
    _save_separate_outputs(branch, separate_data, timestamp, base_dir)


def _save_merged_outputs(branch, data_list, ts, base_dir) -> None:
    """Saves merged category-wise transfers."""
    csv_dir = os.path.join(base_dir, "merged", "csv", f"combined_transfers_from_{branch.name}_{ts}")
    excel_dir = os.path.join(base_dir, "merged", "excel", f"combined_transfers_from_{branch.name}_{ts}")
    
    for item in data_list:
        category, df = item['category'], item['df']
        os.makedirs(csv_dir, exist_ok=True)
        csv_path = os.path.join(csv_dir, f"{branch.name}_combined_{category}.csv")
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        os.makedirs(excel_dir, exist_ok=True)
        excel_path = os.path.join(excel_dir, f"{branch.name}_combined_{category}.xlsx")
        save_formatted_excel(df, excel_path)


def _save_separate_outputs(branch, data_list, ts, base_dir) -> None:
    """Saves separate branch-wise transfers."""
    csv_root = os.path.join(base_dir, "separate", "csv", f"transfers_from_{branch.name}_{ts}")
    excel_root = os.path.join(base_dir, "separate", "excel", f"transfers_from_{branch.name}_{ts}")
    
    for item in data_list:
        target, category, df = item['target'], item['category'], item['df']
        
        csv_dir = os.path.join(csv_root, f"to_{target}")
        os.makedirs(csv_dir, exist_ok=True)
        csv_path = os.path.join(csv_dir, f"transfer_from_{branch.name}_to_{target}_{category}_{ts}.csv")
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        excel_dir = os.path.join(excel_root, f"to_{target}")
        os.makedirs(excel_dir, exist_ok=True)
        excel_path = os.path.join(excel_dir, f"transfer_from_{branch.name}_to_{target}_{category}_{ts}.xlsx")
        save_formatted_excel(df, excel_path)
