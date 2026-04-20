"""Transfer persistence logic for saving and splitting transfers."""

import os
import pandas as pd
from typing import List, Dict
from src.domain.models.distribution import Transfer
from src.domain.services.classification.product_classifier import (
    classify_product_type
)
from src.infrastructure.excel.formatter import save_formatted_excel


CATEGORY_NAMES = {
    'tablets_and_capsules': 'all_tablets_and_capsules',
    'injections': 'all_injections',
    'syrups': 'all_syrups',
    'creams': 'all_creams_and_ointments',
    'sachets': 'all_sachets',
    'other': 'all_other_products'
}


def save_step7_transfers(
    transfers: List[Transfer], 
    output_dir: str, 
    excel_dir: str = None,
    timestamp: str = None
) -> None:
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
    
    _save_branch_collections(transfers, output_dir, excel_dir, timestamp)


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
    transfers: List[Transfer], target_name: str = None
) -> pd.DataFrame:
    """Converts a list of transfers to a sorted DataFrame."""
    records = []
    for transfer in transfers:
        records.append({
            'code': transfer.product.code,
            'product_name': transfer.product.name,
            'quantity_to_transfer': transfer.quantity,
            'target_branch': target_name or transfer.to_branch.name,
            'sender_balance': transfer.sender_balance,
            'receiver_balance': transfer.receiver_balance
        })
    df = pd.DataFrame(records)
    if df.empty:
        return df
        
    if target_name is None:
        return df.sort_values(
            ['product_name', 'target_branch'],
            key=lambda col: col.str.lower() if col.name in ['target_branch', 'product_name'] else col
        )
        
    return df.sort_values(
        'product_name', key=lambda col: col.str.lower()
    )


def _save_branch_collections(
    transfers: List[Transfer], 
    output_dir: str, 
    excel_dir: str = None,
    timestamp: str = None
) -> None:
    """Saves aggregated transfers per branch grouped by category."""
    groups = _group_transfers_by_source_and_category(transfers)
    
    for (source, category), items in groups.items():
        folder_name = f"from_{source.lower()}_all_transfers_collection"
        dataframe = _prepare_transfer_dataframe(items)
        category_name = CATEGORY_NAMES.get(category, f"all_{category}")
        
        # Build filename: from_[source]_[category]_[timestamp]
        timestamp_suffix = f"_{timestamp}" if timestamp else ""
        filename = f"from_{source.lower()}_{category_name}{timestamp_suffix}"
        
        # Save CSV
        csv_spec = f"transfers_from_{source}_to_other_branches"
        csv_collection_dir = os.path.join(output_dir, csv_spec, folder_name)
        os.makedirs(csv_collection_dir, exist_ok=True)
        csv_path = os.path.join(csv_collection_dir, f"{filename}.csv")
        dataframe.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        # Save Excel if dir provided
        if excel_dir:
            excel_spec = f"transfers_excel_from_{source}_to_other_branches"
            excel_collection_dir = os.path.join(excel_dir, excel_spec, folder_name)
            os.makedirs(excel_collection_dir, exist_ok=True)
            excel_path = os.path.join(excel_collection_dir, f"{filename}.xlsx")
            save_formatted_excel(dataframe, excel_path)


def _group_transfers_by_source_and_category(transfers: List[Transfer]) -> Dict:
    """Groups transfers by (source, category)."""
    groups = {}
    for transfer in transfers:
        category = classify_product_type(transfer.product.name)
        key = (transfer.from_branch.name, category)
        if key not in groups:
            groups[key] = []
        groups[key].append(transfer)
    return groups


def _save_split_csv(source, target, category, timestamp, dataframe, base_dir):
    """Saves a category-split CSV."""
    directory = os.path.join(
        base_dir, f"transfers_from_{source}_to_other_branches", 
        f"{source}_to_{target}"
    )
    os.makedirs(directory, exist_ok=True)
    filename = f"{source}_to_{target}_{timestamp}_{category}.csv"
    path = os.path.join(directory, filename)
    dataframe.to_csv(path, index=False, encoding='utf-8-sig')


def _save_split_excel(
    source, target, category, timestamp, dataframe, excel_dir
):
    """Saves a category-split Excel."""
    directory = os.path.join(
        excel_dir, f"transfers_excel_from_{source}_to_other_branches", 
        f"{source}_to_{target}"
    )
    os.makedirs(directory, exist_ok=True)
    filename = f"{source}_to_{target}_{timestamp}_{category}.xlsx"
    save_formatted_excel(dataframe, os.path.join(directory, filename))
