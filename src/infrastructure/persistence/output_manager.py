"""Logic for discovering and listing output artifacts."""

import os
import re
from typing import List, Dict, Optional


def list_artifacts(
    category_name: str, 
    base_directory: str, 
    patterns: Dict[str, str],
    branch_filter: Optional[str] = None
) -> List[Dict]:
    """Lists available output artifacts for a given category."""
    results = []
    
    for file_format in ['csv', 'excel']:
        format_dir = os.path.join(base_directory, file_format)
        if not os.path.exists(format_dir):
            if base_directory.endswith(file_format):
                format_dir = base_directory
            else:
                continue
        
        prefix = patterns.get(file_format, '')
        sub_pattern = f"{prefix}{branch_filter}" if branch_filter else prefix
        
        if category_name == 'shortage':
            _collect_files_recursive(format_dir, category_name, None, results)
            continue

        _scan_format_directory(
            format_dir, category_name, branch_filter, sub_pattern, results
        )
                        
    return results


def _scan_format_directory(fmt_dir, category, branch_filter, sub_pattern, results) -> None:
    """Scans a format directory (csv/excel) for category-specific files."""
    for item in os.listdir(fmt_dir):
        item_path = os.path.join(fmt_dir, item)
        if not os.path.isdir(item_path):
            continue
            
        if _is_branch_match(category, branch_filter, item, sub_pattern):
            if category == 'separate':
                _scan_separate_targets(item_path, category, branch_filter, item, results)
            else:
                branch_meta = _extract_branch_meta(category, branch_filter, item)
                _collect_files_recursive(item_path, category, branch_meta, results)


def _is_branch_match(category, branch_filter, item, sub_pattern) -> bool:
    """Checks if a directory item matches the branch filter rules."""
    if sub_pattern in item:
        return True
        
    if category == 'transfers' and branch_filter:
        return (
            item.startswith(branch_filter) or 
            f"from_{branch_filter}" in item or
            f"From_{branch_filter}" in item or
            f"transfers_from_{branch_filter}" in item or
            f"transfers_excel_from_{branch_filter}" in item
        )
    return False


def _extract_branch_meta(category, branch_filter, item) -> str:
    """Extracts branch metadata from an item name."""
    if branch_filter:
        return branch_filter
        
    match = re.search(r'from_([a-z_]+)_', item)
    if match:
        extracted = match.group(1).replace('excel_from_', '').replace('from_', '')
        return extracted.split('_to_')[0]
        
    if category == 'transfers' and 'from_' in item and '_to_' in item:
        return item.split('from_')[1].split('_to_')[0]
        
    return item


def _scan_separate_targets(item_path, category, branch_filter, item, results) -> None:
    """Special handling for the 'separate' category with another nesting level."""
    for target in os.listdir(item_path):
        target_path = os.path.join(item_path, target)
        if os.path.isdir(target_path) and target.startswith('to_'):
            branch_meta = branch_filter or _extract_branch_meta(category, branch_filter, item)
            _collect_files_recursive(target_path, category, branch_meta, results)


def _collect_files_recursive(search_dir, category, branch_id, results) -> None:
    """Helper to collect files recursively and add metadata."""
    if not os.path.exists(search_dir):
        return
            
    parent = os.path.basename(search_dir)
            
    for item in os.listdir(search_dir):
        path = os.path.join(search_dir, item)
        if os.path.isdir(path):
            _collect_files_recursive(path, category, branch_id, results)
        elif item.endswith(('.csv', '.xlsx')):
            metadata = _create_file_metadata(item, path, category, branch_id, parent)
            if category == 'separate':
                _enrich_separate_metadata(metadata, search_dir, item, parent)
            results.append(metadata)


def _create_file_metadata(name, path, category, branch_id, folder) -> Dict:
    """Creates initial metadata dictionary for an artifact."""
    return {
        'name': name,
        'path': os.path.abspath(path),
        'size': os.path.getsize(path),
        'mtime': os.path.getmtime(path),
        'category': category,
        'branch': branch_id,
        'folder_name': folder
    }


def _enrich_separate_metadata(metadata, search_dir, item, folder) -> None:
    """Adds specific metadata for separate transfers."""
    metadata['source_folder'] = os.path.basename(os.path.dirname(search_dir))
    metadata['target_folder'] = folder
    
    stem = item.split('.')[0]
    if '_to_' in stem:
        parts = stem.split('_')
        try:
            to_idx = parts.index('to')
            metadata['target_branch'] = parts[to_idx + 1]
            metadata['product_category'] = parts[to_idx + 2]
        except (ValueError, IndexError):
            pass
