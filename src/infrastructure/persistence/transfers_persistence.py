"""Transfer persistence logic for saving and splitting transfers."""

import os
import pandas as pd
from typing import List, Dict
from src.domain.models.distribution import Transfer
from src.core.domain.classification.product_classifier import (
    classify_product_type
)
from src.infrastructure.persistence.excel_formatter import save_formatted_excel


def save_step7_transfers(transfers: List[Transfer], output_dir: str) -> None:
    """Saves transfers grouped by source branch (Step 7)."""
    if not transfers:
        return
    branch_pairs = _group_transfers_by_pair(transfers)
    os.makedirs(output_dir, exist_ok=True)
    for (source, target), pair_items in branch_pairs.items():
        dataframe = _prepare_transfer_dataframe(pair_items, target)
        spec = f"transfers_from_{source}_to_other_branches"
        specific_dir = os.path.join(output_dir, spec)
        os.makedirs(specific_dir, exist_ok=True)
        path = os.path.join(specific_dir, f"{source}_to_{target}.csv")
        dataframe.to_csv(path, index=False, encoding='utf-8-sig')


def save_step8_split_transfers(
    transfers: List[Transfer], output_dir: str, excel_dir: str, timestamp: str
) -> None:
    """Saves transfers split by product category (Step 8)."""
    groups = _group_transfers_by_category(transfers)
    for (source, target, category), items in groups.items():
        dataframe = _prepare_transfer_dataframe(items, target)
        _save_split_csv(
            source, target, category, timestamp, dataframe, output_dir
        )
        _save_split_excel(
            source, target, category, timestamp, dataframe, excel_dir
        )


def _group_transfers_by_pair(transfers: List[Transfer]) -> Dict:
    """Groups transfers into (source, target) pairs."""
    pairs = {}
    for transfer in transfers:
        key = (transfer.from_branch.name, transfer.to_branch.name)
        if key not in pairs:
            pairs[key] = []
        pairs[key].append(transfer)
    return pairs


def _group_transfers_by_category(transfers: List[Transfer]) -> Dict:
    """Groups transfers by source, target, and category."""
    groups = {}
    for transfer in transfers:
        category = classify_product_type(transfer.product.name)
        key = (transfer.from_branch.name, transfer.to_branch.name, category)
        if key not in groups:
            groups[key] = []
        groups[key].append(transfer)
    return groups


def _prepare_transfer_dataframe(
    transfers: List[Transfer], target_name: str
) -> pd.DataFrame:
    """Converts a list of transfers to a sorted DataFrame."""
    records = []
    for transfer in transfers:
        records.append({
            'code': transfer.product.code,
            'product_name': transfer.product.name,
            'quantity_to_transfer': transfer.quantity,
            'target_branch': target_name
        })
    return pd.DataFrame(records).sort_values('product_name')


def _save_split_csv(source, target, category, ts, dataframe, base_dir):
    """Saves a category-split CSV."""
    directory = os.path.join(base_dir, f"{source}_to_{target}")
    os.makedirs(directory, exist_ok=True)
    filename = f"{source}_to_{target}_{ts}_{category}.csv"
    path = os.path.join(directory, filename)
    dataframe.to_csv(path, index=False, encoding='utf-8-sig')


def _save_split_excel(source, target, category, ts, dataframe, excel_dir):
    """Saves a category-split Excel."""
    directory = os.path.join(
        excel_dir, f"transfers_excel_from_{source}_to_other_branches", 
        f"{source}_to_{target}"
    )
    os.makedirs(directory, exist_ok=True)
    filename = f"{source}_to_{target}_{ts}_{category}.xlsx"
    save_formatted_excel(dataframe, os.path.join(directory, filename))
