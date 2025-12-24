"""Persistence logic for surplus reports."""

import os
import pandas as pd
from datetime import datetime
from typing import List, Dict
from src.domain.models.distribution import DistributionResult
from src.domain.services.classification.product_classifier import (
    classify_product_type
)


def save_surplus_reports(
    results: List[DistributionResult], 
    base_dir: str
) -> None:
    """Saves surplus reports split by branch and category."""
    today = datetime.now().strftime("%Y%m%d")
    grouped = _group_surplus_by_branch_category(results)
    
    for branch, categories in grouped.items():
        all_items = []
        for category, items in categories.items():
            all_items.extend(items)
            _persist_category_surplus(branch, category, today, items, base_dir)
        
        if all_items:
            _persist_total_branch_surplus(branch, today, all_items, base_dir)


def _group_surplus_by_branch_category(
    results: List[DistributionResult]
) -> Dict:
    """Groups surplus data by branch and then by category."""
    grouped = {}
    for result in results:
        category = classify_product_type(result.product.name)
        for branch, surplus in result.remaining_branch_surplus.items():
            if surplus <= 0:
                continue
            if branch not in grouped:
                grouped[branch] = {}
            if category not in grouped[branch]:
                grouped[branch][category] = []
            
            grouped[branch][category].append({
                'code': result.product.code,
                'product_name': result.product.name,
                'remaining_surplus': surplus
            })
    return grouped


def _persist_category_surplus(branch, category, date, items, base_dir):
    """Saves surplus CSV and Excel for a specific branch/category."""
    dataframe = pd.DataFrame(items).sort_values('product_name')
    
    path_csv = os.path.join(base_dir, "csv", branch)
    os.makedirs(path_csv, exist_ok=True)
    filename_csv = f"remaining_surplus_{branch}_{category}_{date}.csv"
    dataframe.to_csv(
        os.path.join(path_csv, filename_csv), index=False, encoding='utf-8-sig'
    )
    
    path_excel = os.path.join(base_dir, "excel", branch)
    os.makedirs(path_excel, exist_ok=True)
    filename_excel = f"remaining_surplus_{branch}_{category}_{date}.xlsx"
    dataframe.to_excel(
        os.path.join(path_excel, filename_excel), 
        index=False
    )


def _persist_total_branch_surplus(branch, date, items, base_dir):
    """Saves a consolidated surplus file for an entire branch."""
    dataframe = pd.DataFrame(items).sort_values('product_name')
    
    csv_dir = os.path.join(base_dir, "csv", branch)
    csv_filename = f"remaining_surplus_{branch}_total_{date}.csv"
    csv_path = os.path.join(csv_dir, csv_filename)
    dataframe.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    excel_folder = os.path.join(base_dir, "excel", branch)
    excel_filename = f"remaining_surplus_{branch}_total_{date}.xlsx"
    excel_path = os.path.join(excel_folder, excel_filename)
    dataframe.to_excel(excel_path, index=False)
