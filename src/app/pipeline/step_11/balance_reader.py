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


def get_branch_balances(analytics_dir: str, branch: str) -> Dict[str, float]:
    """
    Get balance data for a branch from its analytics file.
    
    Args:
        analytics_dir: Directory containing analytics files
        branch: Branch name
        
    Returns:
        Dictionary mapping product code to balance
    """
    branch_dir = os.path.join(analytics_dir, branch)
    
    if not os.path.exists(branch_dir):
        logger.debug(f"Analytics directory not found for {branch}")
        return {}
    
    # Get latest analytics file
    latest_file = get_latest_file(branch_dir, '.csv')
    
    if not latest_file:
        logger.debug(f"No analytics file found for {branch}")
        return {}
    
    try:
        # Read analytics file
        filepath = os.path.join(branch_dir, latest_file)
        
        # Try to detect if there's a date header
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            first_line = f.readline()
        
        # Skip header if it's a date line
        skiprows = 1 if 'من' in first_line or 'إلى' in first_line else 0
        
        df = pd.read_csv(filepath, skiprows=skiprows, encoding='utf-8-sig')
        
        # Create balance dictionary
        balances = {}
        
        if 'code' in df.columns and 'balance' in df.columns:
            # Ensure balance is numeric
            df['balance'] = pd.to_numeric(df['balance'], errors='coerce').fillna(0)
            
            for _, row in df.iterrows():
                code = str(row['code'])
                balance = float(row['balance'])
                balances[code] = balance
        
        logger.debug(f"Loaded {len(balances)} balance entries for {branch}")
        return balances
        
    except Exception as e:
        logger.warning(f"Error reading balances for {branch}: {e}")
        return {}


def get_all_branches_balances(analytics_dir: str, branches: list) -> Dict[str, Dict[str, float]]:
    """
    Get balance data for all branches.
    
    Args:
        analytics_dir: Directory containing analytics files
        branches: List of branch names
        
    Returns:
        Dictionary mapping branch name to balance dictionary
    """
    all_balances = {}
    
    for branch in branches:
        all_balances[branch] = get_branch_balances(analytics_dir, branch)
    
    return all_balances
