"""Persistence logic for surplus reports."""

import os
import pandas as pd
from datetime import datetime
from typing import List, Dict
from src.domain.models.distribution import DistributionResult
from src.domain.services.classification.product_classifier import (
    classify_product_type
)
from src.shared.collections import group_by
from src.shared.persistence import save_dual_format


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
    flat = []
    for result in results:
        category = classify_product_type(result.product.name)
        for branch, surplus in result.remaining_branch_surplus.items():
            if surplus > 0:
                flat.append((branch, category, {
                    'code': result.product.code,
                    'product_name': result.product.name,
                    'remaining_surplus': surplus,
                }))

    by_branch = group_by(flat, key_func=lambda t: t[0])
    nested: Dict = {}
    for branch, triples in by_branch.items():
        by_cat = group_by(triples, key_func=lambda t: t[1])
        nested[branch] = {cat: [t[2] for t in rows] for cat, rows in by_cat.items()}
    return nested


def _persist_category_surplus(branch, category, date, items, base_dir):
    """Saves surplus CSV and Excel for a specific branch/category."""
    dataframe = pd.DataFrame(items).sort_values(
        'product_name', key=lambda col: col.str.lower()
    )
    save_dual_format(
        dataframe,
        csv_dir=os.path.join(base_dir, "csv", branch),
        excel_dir=os.path.join(base_dir, "excel", branch),
        filename_stem=f"remaining_surplus_{branch}_{category}_{date}",
    )


def _persist_total_branch_surplus(branch, date, items, base_dir):
    """Saves a consolidated surplus file for an entire branch."""
    dataframe = pd.DataFrame(items).sort_values(
        'product_name', key=lambda col: col.str.lower()
    )
    save_dual_format(
        dataframe,
        csv_dir=os.path.join(base_dir, "csv", branch),
        excel_dir=os.path.join(base_dir, "excel", branch),
        filename_stem=f"remaining_surplus_{branch}_total_{date}",
    )
