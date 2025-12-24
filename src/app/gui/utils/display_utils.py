"""Shared utilities for GUI display components."""

import os
import re
from typing import List, Dict


def extract_clean_branch_name(branch_key: str) -> str:
    """
    Extract a clean branch key from potential folder names.
    e.g. 'combined_transfers_from_admin_20251224_082047' -> 'admin'
    """
    match = re.search(r'from_([a-z]+)_', branch_key)
    if match:
        return match.group(1)
    return branch_key


def prepare_zip_paths(files: List[Dict], path_strategy: str = 'flat') -> None:
    """
    Prepares zip_path for a list of files based on the specified strategy.
    
    Strategies:
        'flat': Uses a simple 'folder/name' structure.
        'transfer': Extracts 'from_X_to_Y' from paths for folder structure.
        'nested': Uses 'source/target/name' for deeper nesting.
    """
    for file_info in files:
        if path_strategy == 'transfer':
            _set_transfer_zip_path(file_info)
        elif path_strategy == 'nested':
            _set_nested_zip_path(file_info)
        else:
            _set_flat_zip_path(file_info)


def _set_flat_zip_path(file_info: Dict) -> None:
    """Sets a flat zip path structure."""
    file_info['zip_path'] = os.path.join(
        file_info.get('folder_name', ''), 
        file_info['name']
    )


def _set_transfer_zip_path(file_info: Dict) -> None:
    """Sets zip path by extracting transfer direction from relative path."""
    combined_path = file_info.get('relative_path', '') + file_info['name']
    match = re.search(r'(from_\w+_to_\w+)', combined_path)
    folder = match.group(1) if match else 'other'
    file_info['zip_path'] = os.path.join(folder, file_info['name'])


def _set_nested_zip_path(file_info: Dict) -> None:
    """Sets a nested zip path (source/target/name)."""
    file_info['zip_path'] = os.path.join(
        file_info.get('source_folder', 'unknown'), 
        file_info.get('target_folder', 'unknown'), 
        file_info['name']
    )
