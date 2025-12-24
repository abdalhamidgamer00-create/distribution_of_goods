"""Persistence logic for shortage reports."""

import os
import pandas as pd
from datetime import datetime
from typing import List, Dict
from src.domain.models.distribution import DistributionResult
from src.domain.services.classification.product_classifier import (
    classify_product_type
)
from src.app.gui.utils.translations import BRANCH_NAMES, COLUMNS
from src.shared.constants import BRANCHES


def save_shortage_reports(
    results: List[DistributionResult], 
    base_dir: str
) -> None:
    """Saves shortage reports split by category."""
    today = datetime.now().strftime("%Y%m%d")
    grouped = _group_shortage_by_category(results)
    all_items = []
    
    for category, items in grouped.items():
        all_items.extend(items)
        _persist_category_shortage(category, today, items, base_dir)
        
    if all_items:
        _persist_total_shortage_report(today, all_items, base_dir)


def _group_shortage_by_category(results: List[DistributionResult]) -> Dict:
    """Groups shortage data by category."""
    grouped = {}
    for result in results:
        if result.remaining_needed > 0:
            category = classify_product_type(result.product.name)
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(_format_shortage_row(result))
    return grouped


def _format_shortage_row(result: DistributionResult) -> Dict:
    """Formats a single row for the shortage report."""
    row = {
        COLUMNS['code']: result.product.code,
        COLUMNS['product_name']: result.product.name,
        COLUMNS['shortage_quantity']: result.remaining_needed,
        COLUMNS['total_sales']: result.total_sales
    }
    for branch_key in BRANCHES:
        branch_display = BRANCH_NAMES.get(branch_key, branch_key)
        column_name = f"رصيد {branch_display}"
        balances = result.branch_balances or {}
        row[column_name] = balances.get(branch_key, 0.0)
    return row


def _persist_category_shortage(category, date, items, base_dir):
    """Saves category-split shortage report."""
    dataframe = pd.DataFrame(items).sort_values(
        COLUMNS['shortage_quantity'], ascending=False
    )
    
    csv_dir = os.path.join(base_dir, "csv")
    os.makedirs(csv_dir, exist_ok=True)
    csv_filename = f"total_shortage_{category}_{date}.csv"
    dataframe.to_csv(
        os.path.join(csv_dir, csv_filename), index=False, encoding='utf-8-sig'
    )
    
    excel_dir = os.path.join(base_dir, "excel")
    os.makedirs(excel_dir, exist_ok=True)
    excel_filename = f"total_shortage_{category}_{date}.xlsx"
    dataframe.to_excel(
        os.path.join(excel_dir, excel_filename), 
        index=False
    )


def _persist_total_shortage_report(date, items, base_dir):
    """Saves the global consolidated shortage report."""
    dataframe = pd.DataFrame(items).sort_values(
        COLUMNS['shortage_quantity'], ascending=False
    )
    
    filename = f"shortage_report_total_{date}.csv"
    csv_path = os.path.join(base_dir, "csv", filename)
    dataframe.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    excel_path = os.path.join(
        base_dir, "excel", f"shortage_report_total_{date}.xlsx"
    )
    dataframe.to_excel(excel_path, index=False)
