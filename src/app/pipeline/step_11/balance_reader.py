"""
Balance reader for Step 11

Reads branch balance data from analytics files.
"""

import os
import pandas as pd
from typing import Dict
from src.shared.utils.logging_utils import get_logger
from src.shared.utils.file_handler import get_latest_file

logger = get_logger(__name__)


def _detect_header_skiprows(filepath: str) -> int:
    """Detect if file has date header and return skiprows value."""
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline()
        return 1 if 'من' in first_line or 'إلى' in first_line else 0
    except Exception:
        return 0


def _build_balance_dict(df) -> dict:
    """Build balance dictionary from DataFrame."""
    if 'code' not in df.columns or 'balance' not in df.columns:
        return {}
    
    df['balance'] = pd.to_numeric(df['balance'], errors='coerce').fillna(0)
    return {str(row['code']): float(row['balance']) for _, row in df.iterrows()}


def _read_balance_file(branch_dir: str, latest_file: str, branch: str) -> dict:
    """Read balance file and return balance dictionary."""
    try:
        filepath = os.path.join(branch_dir, latest_file)
        skiprows = _detect_header_skiprows(filepath)
        df = pd.read_csv(filepath, skiprows=skiprows, encoding='utf-8-sig')
        balances = _build_balance_dict(df)
        logger.debug(f"Loaded {len(balances)} balance entries for {branch}")
        return balances
    except Exception as e:
        logger.warning(f"Error reading balances for {branch}: {e}")
        return {}


def get_branch_balances(analytics_dir: str, branch: str) -> Dict[str, float]:
    """Get balance data for a branch from its analytics file."""
    branch_dir = os.path.join(analytics_dir, branch)
    if not os.path.exists(branch_dir):
        logger.debug(f"Analytics directory not found for {branch}")
        return {}
    latest_file = get_latest_file(branch_dir, '.csv')
    if not latest_file:
        logger.debug(f"No analytics file found for {branch}")
        return {}
    return _read_balance_file(branch_dir, latest_file, branch)


def get_all_branches_balances(analytics_dir: str, branches: list) -> Dict[str, Dict[str, float]]:
    """Get balance data for all branches."""
    return {branch: get_branch_balances(analytics_dir, branch) for branch in branches}
