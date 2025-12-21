"""
File combiner for Step 11

Combines regular transfer files with remaining surplus (directed to admin).
"""

import os
from datetime import datetime
import pandas as pd
from typing import Optional, List, Dict
from src.shared.utils.logging_utils import get_logger
from src.shared.utils.file_handler import get_latest_file
from src.app.pipeline.step_11.balance_reader import get_branch_balances

logger = get_logger(__name__)

# Product types for categorization
PRODUCT_TYPES = ['tablets_and_capsules', 'injections', 'syrups', 'creams', 'sachets', 'other']

def get_timestamp() -> str:
    """Get current timestamp for filenames."""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def combine_transfers_and_surplus(
    branch: str,
    transfers_dir: str,
    surplus_dir: str,
    analytics_dir: str,
) -> Optional[pd.DataFrame]:
    """
    Combine transfers and remaining surplus for a branch.
    
    Args:
        branch: Source branch name
        transfers_dir: Directory containing transfer CSV files
        surplus_dir: Directory containing remaining surplus CSV files
        analytics_dir: Directory containing analytics files (for balances)
        
    Returns:
        Combined DataFrame or None if no data
    """
    all_data = []
    
    # 1. Read transfer files (normal transfers to other branches)
    transfers_df = _read_transfer_files(branch, transfers_dir, analytics_dir)
    if transfers_df is not None and not transfers_df.empty:
        all_data.append(transfers_df)
    
    # 2. Read remaining surplus (will be sent to admin)
    surplus_df = _read_surplus_as_admin_transfer(branch, surplus_dir, analytics_dir)
    if surplus_df is not None and not surplus_df.empty:
        all_data.append(surplus_df)
    
    if not all_data:
        return None
    
    # Combine all data
    combined = pd.concat(all_data, ignore_index=True)
    
    # Filter out rows where source branch equals target branch (e.g., admin to admin)
    if 'target_branch' in combined.columns:
        combined = combined[combined['target_branch'] != branch]
    
    return combined


def _add_balance_columns(df: pd.DataFrame, sender_balances: dict, receiver_balances: dict) -> pd.DataFrame:
    """Add sender and receiver balance columns to DataFrame."""
    df['sender_balance'] = df['code'].apply(lambda x: sender_balances.get(str(x), 0))
    df['receiver_balance'] = df['code'].apply(lambda x: receiver_balances.get(str(x), 0))
    return df


def _process_single_transfer_file(filepath: str, filename: str, sender_balances: dict, analytics_dir: str) -> Optional[pd.DataFrame]:
    """Process a single transfer file and add required columns."""
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            return None
        
        target_branch = _extract_target_branch(filename)
        receiver_balances = get_branch_balances(analytics_dir, target_branch)
        
        df['target_branch'] = target_branch
        df['transfer_type'] = 'normal'
        return _add_balance_columns(df, sender_balances, receiver_balances)
        
    except Exception as e:
        logger.warning(f"Error reading {filepath}: {e}")
        return None


def _read_transfer_files(branch: str, transfers_dir: str, analytics_dir: str) -> Optional[pd.DataFrame]:
    """Read all transfer files for a branch."""
    branch_transfers_dir = os.path.join(transfers_dir, f"transfers_from_{branch}_to_other_branches")
    
    if not os.path.exists(branch_transfers_dir):
        logger.debug(f"No transfers directory for {branch}: {branch_transfers_dir}")
        return None
    
    sender_balances = get_branch_balances(analytics_dir, branch)
    all_transfers = []
    
    for filename in os.listdir(branch_transfers_dir):
        if not filename.endswith('.csv'):
            continue
        
        filepath = os.path.join(branch_transfers_dir, filename)
        df = _process_single_transfer_file(filepath, filename, sender_balances, analytics_dir)
        if df is not None:
            all_transfers.append(df)
    
    return pd.concat(all_transfers, ignore_index=True) if all_transfers else None


def _normalize_surplus_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize surplus column names to standard quantity columns."""
    surplus_cols = ['surplus_remaining', 'remaining_surplus', 'surplus_quantity']
    for col in surplus_cols:
        if col in df.columns:
            df['quantity'] = df[col]
            df['quantity_to_transfer'] = df[col]
            break
    return df


def _process_single_surplus_file(filepath: str, sender_balances: dict, admin_balances: dict) -> Optional[pd.DataFrame]:
    """Process a single surplus file and format as admin transfer."""
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            return None
        
        df = _normalize_surplus_columns(df)
        df['target_branch'] = 'admin'
        df['transfer_type'] = 'surplus'
        return _add_balance_columns(df, sender_balances, admin_balances)
        
    except Exception as e:
        logger.warning(f"Error reading {filepath}: {e}")
        return None


def _read_surplus_as_admin_transfer(branch: str, surplus_dir: str, analytics_dir: str) -> Optional[pd.DataFrame]:
    """Read remaining surplus and format as transfer to admin."""
    if branch == 'admin':
        return None
    
    branch_surplus_dir = os.path.join(surplus_dir, branch)
    if not os.path.exists(branch_surplus_dir):
        logger.debug(f"No surplus directory for {branch}")
        return None
    
    sender_balances = get_branch_balances(analytics_dir, branch)
    admin_balances = get_branch_balances(analytics_dir, 'admin')
    all_surplus = []
    
    for filename in os.listdir(branch_surplus_dir):
        if not filename.endswith('.csv'):
            continue
        
        filepath = os.path.join(branch_surplus_dir, filename)
        df = _process_single_surplus_file(filepath, sender_balances, admin_balances)
        if df is not None:
            all_surplus.append(df)
    
    return pd.concat(all_surplus, ignore_index=True) if all_surplus else None


def _extract_target_branch(filename: str) -> str:
    """Extract target branch name from transfer filename."""
    # Remove .csv extension first
    name = filename.replace('.csv', '')
    
    # Pattern: ..._from_X_to_Y or ..._to_Y
    if '_to_' in name:
        parts = name.split('_to_')
        if len(parts) > 1:
            # Get the last part after _to_ and extract first word (branch name)
            target = parts[-1].split('_')[0]
            return target
    return 'unknown'


def generate_merged_files(df: pd.DataFrame, branch: str, csv_output_dir: str, timestamp: str = None) -> List[Dict]:
    """
    Generate merged files (all targets in one file per product type).
    
    Args:
        df: Combined DataFrame
        branch: Source branch name
        csv_output_dir: Output directory
        timestamp: Timestamp for filenames
    
    Returns:
        List of file info dicts
    """
    if df is None or df.empty:
        return []
    
    if timestamp is None:
        timestamp = get_timestamp()
    
    # Create branch output directory with timestamp
    branch_output_dir = os.path.join(csv_output_dir, f"combined_transfers_from_{branch}_{timestamp}")
    os.makedirs(branch_output_dir, exist_ok=True)
    
    files_info = []
    
    # Add product_type column if not present
    if 'product_type' not in df.columns:
        df = _add_product_type_column(df)
    
    # Generate file for each product type
    for product_type in PRODUCT_TYPES:
        type_df = df[df['product_type'] == product_type]
        
        if type_df.empty:
            continue
        
        # Select and order columns
        output_df = _prepare_output_columns(type_df)
        
        # Sort by product_name A to Z (case-insensitive)
        if 'product_name' in output_df.columns:
            output_df = output_df.sort_values(
                'product_name', 
                ascending=True, 
                key=lambda x: x.str.lower()
            )
        
        filename = f"{branch}_combined_{product_type}.csv"
        filepath = os.path.join(branch_output_dir, filename)
        
        output_df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        files_info.append({
            'path': filepath,
            'product_type': product_type,
            'count': len(output_df),
        })
        
        logger.debug(f"Generated merged: {filename} ({len(output_df)} products)")
    
    return files_info


def generate_separate_files(df: pd.DataFrame, branch: str, csv_output_dir: str, timestamp: str = None) -> List[Dict]:
    """
    Generate separate files (one file per target branch per product type).
    Files are organized in subdirectories by target branch.
    
    Structure:
        csv_output_dir/تحويلات_من_{branch}_{timestamp}/{target}/{filename}.csv
    
    Returns:
        List of file info dicts
    """
    if df is None or df.empty:
        return []
    
    if timestamp is None:
        timestamp = get_timestamp()
    
    files_info = []
    
    # Add product_type column if not present
    if 'product_type' not in df.columns:
        df = _add_product_type_column(df)
    
    # Get unique target branches
    target_branches = df['target_branch'].unique()
    
    for target in target_branches:
        # Create subdirectory for each target branch
        source_dir = os.path.join(csv_output_dir, f"transfers_from_{branch}_{timestamp}")
        target_output_dir = os.path.join(source_dir, f"to_{target}")
        os.makedirs(target_output_dir, exist_ok=True)
        
        target_df = df[df['target_branch'] == target]
        
        for product_type in PRODUCT_TYPES:
            type_df = target_df[target_df['product_type'] == product_type]
            
            if type_df.empty:
                continue
            
            # Select and order columns
            output_df = _prepare_output_columns(type_df)
            
            # Sort by product_name A to Z (case-insensitive)
            if 'product_name' in output_df.columns:
                output_df = output_df.sort_values(
                    'product_name', 
                    ascending=True, 
                    key=lambda x: x.str.lower()
                )
            
            filename = f"transfer_from_{branch}_to_{target}_{product_type}_{timestamp}.csv"
            filepath = os.path.join(target_output_dir, filename)
            
            output_df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            files_info.append({
                'path': filepath,
                'product_type': product_type,
                'target': target,
                'count': len(output_df),
            })
    
    return files_info


def _add_product_type_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add product_type column based on unit type."""
    df = df.copy()
    
    def classify_product(row):
        unit = str(row.get('unit', '')).lower() if 'unit' in row else ''
        product_name = str(row.get('product_name', '')).lower()
        
        # Tablets and capsules
        if any(x in unit for x in ['قرص', 'كبسول', 'tab', 'cap']):
            return 'tablets_and_capsules'
        if any(x in product_name for x in ['tab', 'cap', 'قرص', 'كبسول']):
            return 'tablets_and_capsules'
        
        # Injections
        if any(x in unit for x in ['أمبول', 'حقن', 'amp', 'inj', 'vial']):
            return 'injections'
        if any(x in product_name for x in ['amp', 'inj', 'vial', 'أمبول']):
            return 'injections'
        
        # Syrups
        if any(x in unit for x in ['شراب', 'syrup', 'زجاجة']):
            return 'syrups'
        if any(x in product_name for x in ['syrup', 'شراب', 'susp']):
            return 'syrups'
        
        # Creams
        if any(x in unit for x in ['كريم', 'cream', 'مرهم', 'oint']):
            return 'creams'
        if any(x in product_name for x in ['cream', 'oint', 'gel', 'كريم']):
            return 'creams'
        
        # Sachets
        if any(x in unit for x in ['كيس', 'sachet', 'ظرف']):
            return 'sachets'
        if any(x in product_name for x in ['sachet', 'كيس']):
            return 'sachets'
        
        return 'other'
    
    df['product_type'] = df.apply(classify_product, axis=1)
    return df


def _prepare_output_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare and order output columns."""
    # Required columns in order
    required_cols = [
        'code', 'product_name', 'quantity_to_transfer', 'target_branch', 
        'transfer_type', 'sender_balance', 'receiver_balance'
    ]
    
    # Optional columns to include if present
    optional_cols = ['unit', 'selling_price', 'company']
    
    # Build final column list
    final_cols = []
    for col in required_cols:
        if col in df.columns:
            final_cols.append(col)
    
    for col in optional_cols:
        if col in df.columns:
            final_cols.append(col)
    
    return df[final_cols].copy()
