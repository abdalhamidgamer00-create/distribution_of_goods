"""Transfer persistence logic for saving and splitting transfers."""

import os
import pandas as pd
from typing import List, Dict
from src.domain.models.distribution import Transfer
from src.domain.services.classification.product_classifier import (
    classify_product_type
)
from src.infrastructure.excel.formatter import save_formatted_excel
from src.shared.collections import group_by
from src.shared.persistence import save_dual_format


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
    branch_pairs = group_by(
        transfers,
        key_func=lambda t: (t.from_branch.name, t.to_branch.name),
    )
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
    groups = group_by(
        transfers,
        key_func=lambda t: (
            t.from_branch.name,
            t.to_branch.name,
            classify_product_type(t.product.name),
        ),
    )
    for (source, target, category), items in groups.items():
        dataframe = _prepare_transfer_dataframe(items, target)
        stem = f"{source}_to_{target}_{timestamp}_{category}"
        csv_directory = os.path.join(
            output_dir, f"transfers_from_{source}_to_other_branches",
            f"{source}_to_{target}",
        )
        excel_directory = os.path.join(
            excel_dir, f"transfers_excel_from_{source}_to_other_branches",
            f"{source}_to_{target}",
        )
        save_dual_format(
            dataframe, csv_directory, excel_directory, stem,
            excel_writer=save_formatted_excel,
        )


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
    groups = group_by(
        transfers,
        key_func=lambda t: (t.from_branch.name, classify_product_type(t.product.name)),
    )
    
    for (source, category), items in groups.items():
        folder_name = f"from_{source.lower()}_all_transfers_collection"
        dataframe = _prepare_transfer_dataframe(items)
        category_name = CATEGORY_NAMES.get(category, f"all_{category}")
        
        timestamp_suffix = f"_{timestamp}" if timestamp else ""
        filename = f"from_{source.lower()}_{category_name}{timestamp_suffix}"
        
        csv_spec = f"transfers_from_{source}_to_other_branches"
        csv_collection_dir = os.path.join(output_dir, csv_spec, folder_name)
        os.makedirs(csv_collection_dir, exist_ok=True)
        csv_path = os.path.join(csv_collection_dir, f"{filename}.csv")
        dataframe.to_csv(csv_path, index=False, encoding='utf-8-sig')
        
        if excel_dir:
            excel_spec = f"transfers_excel_from_{source}_to_other_branches"
            excel_collection_dir = os.path.join(excel_dir, excel_spec, folder_name)
            os.makedirs(excel_collection_dir, exist_ok=True)
            excel_path = os.path.join(excel_collection_dir, f"{filename}.xlsx")
            save_formatted_excel(dataframe, excel_path)
