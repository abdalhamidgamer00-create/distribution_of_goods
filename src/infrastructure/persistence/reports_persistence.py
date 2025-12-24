"""Persistence logic for surplus and shortage reports."""

import os
import pandas as pd
from datetime import datetime
from typing import List, Dict
from src.domain.models.distribution import DistributionResult
from src.core.domain.classification.product_classifier import classify_product_type
from src.app.gui.utils.translations import BRANCH_NAMES, COLUMNS
from src.shared.constants import BRANCHES


def save_surplus_reports(results: List[DistributionResult], base_dir: str) -> None:
    """Saves surplus reports split by branch and category."""
    timestamp = datetime.now().strftime("%Y%m%d")
    grouped = _group_surplus_by_branch_category(results)
    
    for branch, categories in grouped.items():
        all_items = []
        for category, items in categories.items():
            all_items.extend(items)
            _save_category_surplus(branch, category, timestamp, items, base_dir)
        
        if all_items:
            _save_total_branch_surplus(branch, timestamp, all_items, base_dir)


def save_shortage_reports(results: List[DistributionResult], base_dir: str) -> None:
    """Saves shortage reports split by category."""
    timestamp = datetime.now().strftime("%Y%m%d")
    grouped = _group_shortage_by_category(results)
    all_items = []
    
    for category, items in grouped.items():
        all_items.extend(items)
        _save_category_shortage(category, timestamp, items, base_dir)
        
    if all_items:
        _save_total_shortage_report(timestamp, all_items, base_dir)


def _group_surplus_by_branch_category(results: List[DistributionResult]) -> Dict:
    """Groups surplus data by branch and then by category."""
    grouped = {}
    for res in results:
        category = classify_product_type(res.product.name)
        for branch, surplus in res.remaining_branch_surplus.items():
            if surplus <= 0:
                continue
            if branch not in grouped:
                grouped[branch] = {}
            if category not in grouped[branch]:
                grouped[branch][category] = []
            
            grouped[branch][category].append({
                'code': res.product.code,
                'product_name': res.product.name,
                'remaining_surplus': surplus
            })
    return grouped


def _save_category_surplus(branch, category, ts, items, base_dir) -> None:
    """Saves surplus CSV and Excel for a specific branch/category."""
    df = pd.DataFrame(items).sort_values('product_name')
    
    # CSV
    path_csv = os.path.join(base_dir, "csv", branch)
    os.makedirs(path_csv, exist_ok=True)
    df.to_csv(os.path.join(path_csv, f"remaining_surplus_{branch}_{category}_{ts}.csv"), 
              index=False, encoding='utf-8-sig')
    
    # Excel
    path_excel = os.path.join(base_dir, "excel", branch)
    os.makedirs(path_excel, exist_ok=True)
    df.to_excel(os.path.join(path_excel, f"remaining_surplus_{branch}_{category}_{ts}.xlsx"), 
                index=False)


def _save_total_branch_surplus(branch, ts, items, base_dir) -> None:
    """Saves a consolidated surplus file for an entire branch."""
    df = pd.DataFrame(items).sort_values('product_name')
    
    csv_path = os.path.join(base_dir, "csv", branch, f"remaining_surplus_{branch}_total_{ts}.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    excel_path = os.path.join(base_dir, "excel", branch, f"remaining_surplus_{branch}_total_{ts}.xlsx")
    df.to_excel(excel_path, index=False)


def _group_shortage_by_category(results: List[DistributionResult]) -> Dict:
    """Groups shortage data by category."""
    grouped = {}
    for res in results:
        if res.remaining_needed > 0:
            category = classify_product_type(res.product.name)
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(_format_shortage_row(res))
    return grouped


def _format_shortage_row(res: DistributionResult) -> Dict:
    """Formats a single row for the shortage report."""
    row = {
        COLUMNS['code']: res.product.code,
        COLUMNS['product_name']: res.product.name,
        COLUMNS['shortage_quantity']: res.remaining_needed,
        COLUMNS['total_sales']: res.total_sales
    }
    for branch_key in BRANCHES:
        col = f"رصيد {BRANCH_NAMES.get(branch_key, branch_key)}"
        row[col] = res.branch_balances.get(branch_key, 0.0) if res.branch_balances else 0.0
    return row


def _save_category_shortage(category, ts, items, base_dir) -> None:
    """Saves category-split shortage report."""
    df = pd.DataFrame(items).sort_values(COLUMNS['shortage_quantity'], ascending=False)
    
    csv_dir = os.path.join(base_dir, "csv")
    os.makedirs(csv_dir, exist_ok=True)
    df.to_csv(os.path.join(csv_dir, f"total_shortage_{category}_{ts}.csv"), 
              index=False, encoding='utf-8-sig')
    
    excel_dir = os.path.join(base_dir, "excel")
    os.makedirs(excel_dir, exist_ok=True)
    df.to_excel(os.path.join(excel_dir, f"total_shortage_{category}_{ts}.xlsx"), 
                index=False)


def _save_total_shortage_report(ts, items, base_dir) -> None:
    """Saves the global consolidated shortage report."""
    df = pd.DataFrame(items).sort_values(COLUMNS['shortage_quantity'], ascending=False)
    
    csv_path = os.path.join(base_dir, "csv", f"shortage_report_total_{ts}.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    excel_path = os.path.join(base_dir, "excel", f"shortage_report_total_{ts}.xlsx")
    df.to_excel(excel_path, index=False)
