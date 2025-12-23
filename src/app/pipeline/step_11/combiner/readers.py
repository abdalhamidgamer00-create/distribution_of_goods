"""Logistical reader for transfers and surplus."""
import os
import pandas as pd
from typing import Optional, Dict
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_11.balance_reader import get_branch_balances
from .processors import (
    extract_target_branch, 
    add_balance_columns, 
    normalize_surplus_columns
)

logger = get_logger(__name__)

def read_transfer_files(branch: str, transfers_dir: str, analytics_dir: str) -> Optional[pd.DataFrame]:
    """Read all transfer files for a branch."""
    branch_transfers_dir = os.path.join(transfers_dir, f"transfers_from_{branch}_to_other_branches")
    
    if not os.path.exists(branch_transfers_dir):
        logger.debug(f"No transfers directory for {branch}: {branch_transfers_dir}")
        return None
    
    sender_balances = get_branch_balances(analytics_dir, branch)
    all_transfers = _collect_transfer_files(branch_transfers_dir, sender_balances, analytics_dir)
    return pd.concat(all_transfers, ignore_index=True) if all_transfers else None


def _collect_transfer_files(branch_transfers_dir: str, sender_balances: Dict, analytics_dir: str) -> list:
    """Collect all transfer DataFrames from directory."""
    all_transfers = []
    for filename in os.listdir(branch_transfers_dir):
        if not filename.endswith('.csv'):
            continue
        filepath = os.path.join(branch_transfers_dir, filename)
        df = _process_single_transfer_file(filepath, filename, sender_balances, analytics_dir)
        if df is not None:
            all_transfers.append(df)
    return all_transfers


def _process_single_transfer_file(filepath: str, filename: str, sender_balances: Dict, analytics_dir: str) -> Optional[pd.DataFrame]:
    """Process a single transfer file and add required columns."""
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            return None
        
        target_branch = extract_target_branch(filename)
        receiver_balances = get_branch_balances(analytics_dir, target_branch)
        df['target_branch'] = target_branch
        df['transfer_type'] = 'normal'
        return add_balance_columns(df, sender_balances, receiver_balances)
    except Exception as e:
        logger.warning(f"Error reading {filepath}: {e}")
        return None


def read_surplus_as_admin_transfer(branch: str, surplus_dir: str, analytics_dir: str) -> Optional[pd.DataFrame]:
    """Read remaining surplus and format as transfer to admin."""
    if branch == 'admin':
        return None
    branch_surplus_dir = os.path.join(surplus_dir, branch)
    if not os.path.exists(branch_surplus_dir):
        logger.debug(f"No surplus directory for {branch}")
        return None
    
    sender_balances = get_branch_balances(analytics_dir, branch)
    admin_balances = get_branch_balances(analytics_dir, 'admin')
    all_surplus = _collect_surplus_files(branch_surplus_dir, sender_balances, admin_balances)
    return pd.concat(all_surplus, ignore_index=True) if all_surplus else None


def _collect_surplus_files(branch_surplus_dir: str, sender_balances: Dict, admin_balances: Dict) -> list:
    """Collect all surplus DataFrames from directory."""
    all_surplus = []
    for filename in os.listdir(branch_surplus_dir):
        if not filename.endswith('.csv'):
            continue
        filepath = os.path.join(branch_surplus_dir, filename)
        try:
            df = pd.read_csv(filepath)
            if df.empty:
                continue
            df = normalize_surplus_columns(df)
            df['target_branch'] = 'admin'
            df['transfer_type'] = 'surplus'
            df = add_balance_columns(df, sender_balances, admin_balances)
            all_surplus.append(df)
        except Exception as e:
            logger.warning(f"Error reading {filepath}: {e}")
    return all_surplus
