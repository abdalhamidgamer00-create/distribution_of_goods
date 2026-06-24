"""Persistence logic for shortage reports."""

import os
import pandas as pd
from datetime import datetime
from typing import List, Dict
from src.domain.models.distribution import DistributionResult
from src.domain.services.classification.product_classifier import (
    classify_product_type
)
from src.presentation.gui.utils.translations import BRANCH_NAMES, COLUMNS
from src.shared.collections import group_by
from src.shared.constants import BRANCHES
from src.shared.persistence import save_dual_format


def save_shortage_reports(
    results: List[DistributionResult], 
    base_dir: str
) -> None:
    """Saves shortage reports split by category."""
    today = datetime.now().strftime("%Y%m%d")
    grouped = group_by(
        [_format_shortage_row(r) for r in results if r.remaining_shortage > 0],
        key_func=lambda row: row.pop("_category"),
    )
    all_items = []
    
    for category, items in grouped.items():
        all_items.extend(items)
        _persist_category_shortage(category, today, items, base_dir)
        
    if all_items:
        _persist_total_shortage_report(today, all_items, base_dir)


def _format_shortage_row(result: DistributionResult) -> Dict:
    """Formats a single row for the shortage report."""
    row = {
        "_category": classify_product_type(result.product.name),
        COLUMNS['code']: result.product.code,
        COLUMNS['product_name']: result.product.name,
        COLUMNS['shortage_quantity']: result.remaining_shortage,
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
    save_dual_format(
        dataframe,
        csv_dir=os.path.join(base_dir, "csv"),
        excel_dir=os.path.join(base_dir, "excel"),
        filename_stem=f"total_shortage_{category}_{date}",
    )


def _persist_total_shortage_report(date, items, base_dir):
    """Saves the global consolidated shortage report."""
    dataframe = pd.DataFrame(items).sort_values(
        COLUMNS['shortage_quantity'], ascending=False
    )
    save_dual_format(
        dataframe,
        csv_dir=os.path.join(base_dir, "csv"),
        excel_dir=os.path.join(base_dir, "excel"),
        filename_stem=f"shortage_report_total_{date}",
    )
