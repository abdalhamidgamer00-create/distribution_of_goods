"""Persistence logic for combined transfers (Step 11)."""

import os
import pandas as pd
from typing import List, Dict
from src.domain.models.entities import Branch
from src.infrastructure.excel.formatter import save_formatted_excel


def save_step11_combined_transfers(
    branch_entity: Branch,
    merged_items: List[Dict], 
    separate_items: List[Dict],
    timestamp_string: str,
    base_output_dir: str = "data/output/combined_transfers"
) -> None:
    """Saves combined transfers (merged and separate) precisely."""
    _persist_merged_outputs(
        branch_entity, merged_items, timestamp_string, base_output_dir
    )
    _persist_separate_outputs(
        branch_entity, separate_items, timestamp_string, base_output_dir
    )


def _persist_merged_outputs(branch, items, timestamp, base_dir) -> None:
    """Saves merged category-wise transfers to CSV and Excel."""
    folder_name = f"combined_transfers_from_{branch.name}_{timestamp}"
    csv_dir = os.path.join(base_dir, "merged", "csv", folder_name)
    excel_dir = os.path.join(base_dir, "merged", "excel", folder_name)
    
    for entry in items:
        category, dataframe = entry['category'], entry['dataframe']
        os.makedirs(csv_dir, exist_ok=True)
        filename_csv = f"{branch.name}_combined_{category}.csv"
        dataframe.to_csv(
            os.path.join(csv_dir, filename_csv), 
            index=False, 
            encoding='utf-8-sig'
        )
        
        os.makedirs(excel_dir, exist_ok=True)
        filename_excel = f"{branch.name}_combined_{category}.xlsx"
        save_formatted_excel(
            dataframe, os.path.join(excel_dir, filename_excel)
        )


def _persist_separate_outputs(branch, items, timestamp, base_dir) -> None:
    """Saves separate branch-wise transfers to CSV and Excel."""
    folder_name = f"transfers_from_{branch.name}_{timestamp}"
    csv_root = os.path.join(base_dir, "separate", "csv", folder_name)
    excel_root = os.path.join(base_dir, "separate", "excel", folder_name)
    
    for entry in items:
        target, category, dataframe = (
            entry['target'], entry['category'], entry['dataframe']
        )
        _save_individual_target(
            branch.name, target, category, timestamp, dataframe, 
            csv_root, excel_root
        )


def _save_individual_target(
    source, target, category, timestamp, dataframe, csv_root, excel_root
) -> None:
    """Saves files for a specific target branch."""
    csv_dir = os.path.join(csv_root, f"to_{target}")
    os.makedirs(csv_dir, exist_ok=True)
    csv_filename = (
        f"transfer_from_{source}_to_{target}_{category}_{timestamp}.csv"
    )
    dataframe.to_csv(
        os.path.join(csv_dir, csv_filename), 
        index=False, 
        encoding='utf-8-sig'
    )
    
    excel_dir = os.path.join(excel_root, f"to_{target}")
    os.makedirs(excel_dir, exist_ok=True)
    excel_filename = (
        f"transfer_from_{source}_to_{target}_{category}_{timestamp}.xlsx"
    )
    save_formatted_excel(dataframe, os.path.join(excel_dir, excel_filename))
