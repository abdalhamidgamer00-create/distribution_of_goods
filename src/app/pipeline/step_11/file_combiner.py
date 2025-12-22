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


# =============================================================================
# CONSTANTS
# =============================================================================

# Product types for categorization
PRODUCT_TYPES = ['tablets_and_capsules', 'injections', 'syrups', 'creams', 'sachets', 'other']

# Classification keywords for product type detection
PRODUCT_TYPE_KEYWORDS = {
    'tablets_and_capsules': (['قرص', 'كبسول', 'tab', 'cap'], ['tab', 'cap', 'قرص', 'كبسول']),
    'injections': (['أمبول', 'حقن', 'amp', 'inj', 'vial'], ['amp', 'inj', 'vial', 'أمبول']),
    'syrups': (['شراب', 'syrup', 'زجاجة'], ['syrup', 'شراب', 'susp']),
    'creams': (['كريم', 'cream', 'مرهم', 'oint'], ['cream', 'oint', 'gel', 'كريم']),
    'sachets': (['كيس', 'sachet', 'ظرف'], ['sachet', 'كيس']),
}


# =============================================================================
# PUBLIC API
# =============================================================================

def get_timestamp() -> str:
    """Get current timestamp for filenames."""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def combine_transfers_and_surplus(
    branch: str, transfers_dir: str, surplus_dir: str, analytics_dir: str,
) -> Optional[pd.DataFrame]:
    """Combine transfers and remaining surplus for a branch."""
    all_data = _collect_transfer_and_surplus_data(branch, transfers_dir, surplus_dir, analytics_dir)
    if not all_data:
        return None
    
    combined = pd.concat(all_data, ignore_index=True)
    return _filter_self_transfers(combined, branch)


def generate_merged_files(df: pd.DataFrame, branch: str, csv_output_dir: str, timestamp: str = None) -> List[Dict]:
    """Generate merged files (all targets in one file per product type)."""
    if df is None or df.empty:
        return []
    timestamp = timestamp or get_timestamp()
    branch_output_dir = os.path.join(csv_output_dir, f"combined_transfers_from_{branch}_{timestamp}")
    os.makedirs(branch_output_dir, exist_ok=True)
    if 'product_type' not in df.columns:
        df = _add_product_type_column(df)
    return _create_merged_files(df, branch, branch_output_dir)


def generate_separate_files(df: pd.DataFrame, branch: str, csv_output_dir: str, timestamp: str = None) -> List[Dict]:
    """Generate separate files (one file per target branch per product type)."""
    if df is None or df.empty:
        return []
    
    timestamp = timestamp or get_timestamp()
    
    if 'product_type' not in df.columns:
        df = _add_product_type_column(df)
    
    return _create_separate_files(df, branch, csv_output_dir, timestamp)


# =============================================================================
# DATA COLLECTION HELPERS
# =============================================================================

def _collect_transfer_and_surplus_data(branch: str, transfers_dir: str, surplus_dir: str, analytics_dir: str) -> list:
    """Collect transfer and surplus data for a branch."""
    all_data = []
    transfers_df = _read_transfer_files(branch, transfers_dir, analytics_dir)
    if transfers_df is not None and not transfers_df.empty:
        all_data.append(transfers_df)
    surplus_df = _read_surplus_as_admin_transfer(branch, surplus_dir, analytics_dir)
    if surplus_df is not None and not surplus_df.empty:
        all_data.append(surplus_df)
    return all_data


def _read_transfer_files(branch: str, transfers_dir: str, analytics_dir: str) -> Optional[pd.DataFrame]:
    """Read all transfer files for a branch."""
    branch_transfers_dir = os.path.join(transfers_dir, f"transfers_from_{branch}_to_other_branches")
    
    if not os.path.exists(branch_transfers_dir):
        logger.debug(f"No transfers directory for {branch}: {branch_transfers_dir}")
        return None
    
    sender_balances = get_branch_balances(analytics_dir, branch)
    all_transfers = _collect_transfer_files(branch_transfers_dir, sender_balances, analytics_dir)
    return pd.concat(all_transfers, ignore_index=True) if all_transfers else None


def _collect_transfer_files(branch_transfers_dir: str, sender_balances: dict, analytics_dir: str) -> list:
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


def _read_surplus_as_admin_transfer(branch: str, surplus_dir: str, analytics_dir: str) -> Optional[pd.DataFrame]:
    """Read remaining surplus and format as transfer to admin."""
    if branch == 'admin':
        return None
    branch_surplus_dir = os.path.join(surplus_dir, branch)
    if not os.path.exists(branch_surplus_dir):
        logger.debug(f"No surplus directory for {branch}")
        return None
    sender_balances, admin_balances = get_branch_balances(analytics_dir, branch), get_branch_balances(analytics_dir, 'admin')
    all_surplus = _collect_surplus_files(branch_surplus_dir, sender_balances, admin_balances)
    return pd.concat(all_surplus, ignore_index=True) if all_surplus else None


def _collect_surplus_files(branch_surplus_dir: str, sender_balances: dict, admin_balances: dict) -> list:
    """Collect all surplus DataFrames from directory."""
    all_surplus = []
    for filename in os.listdir(branch_surplus_dir):
        if not filename.endswith('.csv'):
            continue
        filepath = os.path.join(branch_surplus_dir, filename)
        df = _process_single_surplus_file(filepath, sender_balances, admin_balances)
        if df is not None:
            all_surplus.append(df)
    return all_surplus


# =============================================================================
# DATA PROCESSING HELPERS
# =============================================================================

def _filter_self_transfers(combined: pd.DataFrame, branch: str) -> pd.DataFrame:
    """Filter out self-transfers from combined data."""
    if 'target_branch' in combined.columns:
        return combined[combined['target_branch'] != branch]
    return combined


def _add_balance_columns(df: pd.DataFrame, sender_balances: dict, receiver_balances: dict) -> pd.DataFrame:
    """Add sender and receiver balance columns to DataFrame."""
    df['sender_balance'] = df['code'].apply(lambda x: sender_balances.get(str(x), 0))
    df['receiver_balance'] = df['code'].apply(lambda x: receiver_balances.get(str(x), 0))
    return df


def _normalize_surplus_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize surplus column names to standard quantity columns."""
    surplus_cols = ['surplus_remaining', 'remaining_surplus', 'surplus_quantity']
    for col in surplus_cols:
        if col in df.columns:
            df['quantity'] = df[col]
            df['quantity_to_transfer'] = df[col]
            break
    return df


def _sort_by_product_name(df: pd.DataFrame) -> pd.DataFrame:
    """Sort DataFrame by product_name A to Z (case-insensitive)."""
    if 'product_name' in df.columns:
        return df.sort_values('product_name', ascending=True, key=lambda x: x.str.lower())
    return df


def _extract_target_branch(filename: str) -> str:
    """Extract target branch name from transfer filename."""
    name = filename.replace('.csv', '')  # Remove .csv extension first
    # Pattern: ..._from_X_to_Y or ..._to_Y
    if '_to_' in name:
        parts = name.split('_to_')
        if len(parts) > 1:
            return parts[-1].split('_')[0]  # Get first word after _to_
    return 'unknown'


# =============================================================================
# FILE I/O HELPERS
# =============================================================================

def _read_and_enrich_transfer(filepath: str, filename: str, sender_balances: dict, analytics_dir: str) -> Optional[pd.DataFrame]:
    """Read and enrich transfer file with balance columns."""
    df = pd.read_csv(filepath)
    if df.empty:
        return None
    
    target_branch = _extract_target_branch(filename)
    receiver_balances = get_branch_balances(analytics_dir, target_branch)
    df['target_branch'] = target_branch
    df['transfer_type'] = 'normal'
    return _add_balance_columns(df, sender_balances, receiver_balances)


def _process_single_transfer_file(filepath: str, filename: str, sender_balances: dict, analytics_dir: str) -> Optional[pd.DataFrame]:
    """Process a single transfer file and add required columns."""
    try:
        return _read_and_enrich_transfer(filepath, filename, sender_balances, analytics_dir)
    except Exception as e:
        logger.warning(f"Error reading {filepath}: {e}")
        return None


def _read_and_process_surplus(filepath: str, sender_balances: dict, admin_balances: dict) -> Optional[pd.DataFrame]:
    """Read surplus file and process it."""
    df = pd.read_csv(filepath)
    if df.empty:
        return None
    
    df = _normalize_surplus_columns(df)
    df['target_branch'] = 'admin'
    df['transfer_type'] = 'surplus'
    return _add_balance_columns(df, sender_balances, admin_balances)


def _process_single_surplus_file(filepath: str, sender_balances: dict, admin_balances: dict) -> Optional[pd.DataFrame]:
    """Process a single surplus file and format as admin transfer."""
    try:
        return _read_and_process_surplus(filepath, sender_balances, admin_balances)
    except Exception as e:
        logger.warning(f"Error reading {filepath}: {e}")
        return None


# =============================================================================
# OUTPUT GENERATION HELPERS
# =============================================================================

def _create_merged_files(df: pd.DataFrame, branch: str, branch_output_dir: str) -> List[Dict]:
    """Create merged files for each product type."""
    files_info = []
    for product_type in PRODUCT_TYPES:
        filename = f"{branch}_combined_{product_type}.csv"
        filepath = os.path.join(branch_output_dir, filename)
        file_info = _process_product_type_file(df, product_type, filepath)
        if file_info:
            files_info.append(file_info)
            logger.debug(f"Generated merged: {filename} ({file_info['count']} products)")
    return files_info


def _process_product_type_file(df: pd.DataFrame, product_type: str, filepath: str) -> Optional[dict]:
    """Process and save a product type file, return file info."""
    type_df = df[df['product_type'] == product_type]
    if type_df.empty:
        return None
    output_df = _sort_by_product_name(_prepare_output_columns(type_df))
    output_df.to_csv(filepath, index=False, encoding='utf-8-sig')
    return {'path': filepath, 'product_type': product_type, 'count': len(output_df)}


def _create_separate_files(df: pd.DataFrame, branch: str, csv_output_dir: str, timestamp: str) -> List[Dict]:
    """Create separate files for each target branch."""
    files_info = []
    source_dir = os.path.join(csv_output_dir, f"transfers_from_{branch}_{timestamp}")
    for target in df['target_branch'].unique():
        target_output_dir = os.path.join(source_dir, f"to_{target}")
        os.makedirs(target_output_dir, exist_ok=True)
        files_info.extend(_process_target_branch_files(df, target, branch, target_output_dir, timestamp))
    return files_info


def _process_target_branch_files(df: pd.DataFrame, target: str, branch: str, target_output_dir: str, timestamp: str) -> List[Dict]:
    """Process all product type files for a target branch."""
    target_df = df[df['target_branch'] == target]
    files_info = []
    
    for product_type in PRODUCT_TYPES:
        result = _process_separate_product_file(target_df, product_type, branch, target, target_output_dir, timestamp)
        if result:
            files_info.append(result)
    
    return files_info


def _process_separate_product_file(target_df: pd.DataFrame, product_type: str, branch: str, target: str, 
                                 target_output_dir: str, timestamp: str) -> dict:
    """Process a single product type file."""
    type_df = target_df[target_df['product_type'] == product_type]
    if type_df.empty:
        return None
    
    output_df = _sort_by_product_name(_prepare_output_columns(type_df))
    filename = f"transfer_from_{branch}_to_{target}_{product_type}_{timestamp}.csv"
    filepath = os.path.join(target_output_dir, filename)
    return _save_and_record_file(output_df, filepath, product_type, target)


def _save_and_record_file(output_df: pd.DataFrame, filepath: str, product_type: str, target: str) -> dict:
    """Save DataFrame to file and return file info."""
    output_df.to_csv(filepath, index=False, encoding='utf-8-sig')
    return {'path': filepath, 'product_type': product_type, 'target': target, 'count': len(output_df)}


# =============================================================================
# CLASSIFICATION HELPERS
# =============================================================================

def _classify_by_keywords(unit: str, product_name: str) -> str:
    """Classify product based on unit and product name keywords."""
    for category, (unit_keywords, name_keywords) in PRODUCT_TYPE_KEYWORDS.items():
        if any(keyword in unit for keyword in unit_keywords):
            return category
        if any(keyword in product_name for keyword in name_keywords):
            return category
    return 'other'


def _add_product_type_column(df: pd.DataFrame) -> pd.DataFrame:
    """Add product_type column based on unit type."""
    df = df.copy()
    
    def classify_product(row):
        unit = str(row.get('unit', '')).lower() if 'unit' in row else ''
        product_name = str(row.get('product_name', '')).lower()
        return _classify_by_keywords(unit, product_name)
    
    df['product_type'] = df.apply(classify_product, axis=1)
    return df


# =============================================================================
# OUTPUT COLUMN HELPERS
# =============================================================================

def _build_column_list(df: pd.DataFrame, required_cols: list, optional_cols: list) -> list:
    """Build final column list from available columns."""
    final_cols = [col for col in required_cols if col in df.columns]
    final_cols.extend(col for col in optional_cols if col in df.columns)
    return final_cols


def _prepare_output_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare and order output columns."""
    required_cols = ['code', 'product_name', 'quantity_to_transfer', 'target_branch', 
                     'transfer_type', 'sender_balance', 'receiver_balance']
    optional_cols = ['unit', 'selling_price', 'company']
    final_cols = _build_column_list(df, required_cols, optional_cols)
    return df[final_cols].copy()
