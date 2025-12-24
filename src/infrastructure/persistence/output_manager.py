"""Logic for discovering and listing output artifacts."""

import os
import re
from typing import List, Dict, Optional
from src.infrastructure.persistence.artifact_metadata import (
    create_artifact_metadata as create_m, enrich_separate_metadata as enrich_m
)


def list_artifacts(
    category_name: str, base_directory: str, 
    patterns: Dict[str, str], branch_filter: Optional[str] = None
) -> List[Dict]:
    """Lists available output artifacts for a given category."""
    results = []
    for f_fmt in ['csv', 'excel']:
        fmt_dir = _resolve_format_dir(base_directory, f_fmt)
        if not fmt_dir:
            continue
        prefix = patterns.get(f_fmt, '')
        pat = f"{prefix}{branch_filter}" if branch_filter else prefix
        if category_name == 'shortage':
            _collect_recursive(fmt_dir, category_name, None, results)
        else:
            _scan_directory(fmt_dir, category_name, branch_filter, pat, results)
    return results


def _resolve_format_dir(base, file_format) -> Optional[str]:
    """Resolves the directory for a specific file format."""
    directory = os.path.join(base, file_format)
    if os.path.exists(directory):
        return directory
    return base if base.endswith(file_format) and os.path.exists(base) else None


def _scan_directory(dir_path, category, filter_val, pattern, results) -> None:
    """Scans a directory for matching artifact subdirectories."""
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if not os.path.isdir(item_path):
            continue
        if _is_match(category, filter_val, item, pattern):
            if category == 'separate':
                _scan_separate(item_path, category, filter_val, item, results)
            else:
                branch = _extract_meta(category, filter_val, item)
                _collect_recursive(item_path, category, branch, results)


def _is_match(category, filter_val, item, pattern) -> bool:
    """Checks if a directory item matches the search pattern."""
    if pattern in item:
        return True
    if category == 'transfers' and filter_val:
        v = filter_val
        is_f = f"from_{v}" in item or f"From_{v}" in item
        is_l = (f"transfers_from_{v}" in item or 
                f"transfers_excel_from_{v}" in item)
        return item.startswith(v) or is_f or is_l
    return False


def _extract_meta(category, filter_val, item) -> str:
    """Extracts branch metadata from an item name."""
    if filter_val:
        return filter_val
    match = re.search(r'from_([a-z_]+)_', item)
    if match:
        name = match.group(1).replace('excel_from_', '').replace('from_', '')
        return name.split('_to_')[0]
    return item.split('from_')[1].split('_to_')[0] if 'from_' in item else item


def _scan_separate(path, category, filter_val, item, results) -> None:
    """Specialized scan for separate transfers."""
    for target in os.listdir(path):
        target_path = os.path.join(path, target)
        if os.path.isdir(target_path) and target.startswith('to_'):
            branch = filter_val or _extract_meta(category, filter_val, item)
            _collect_recursive(target_path, category, branch, results)


def _collect_recursive(search_dir, category, branch, results) -> None:
    """Recursively collects files and applies metadata enrichment."""
    if not os.path.exists(search_dir):
        return
    folder = os.path.basename(search_dir)
    for item in os.listdir(search_dir):
        path = os.path.join(search_dir, item)
        if os.path.isdir(path):
            _collect_recursive(path, category, branch, results)
        elif item.endswith(('.csv', '.xlsx')):
            meta = create_m(item, path, category, branch, folder)
            if category == 'separate':
                enrich_m(meta, search_dir, item, folder)
            results.append(meta)
