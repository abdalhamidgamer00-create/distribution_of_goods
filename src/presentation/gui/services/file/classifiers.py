"""File classification logic."""
import os
from typing import Dict, Optional
from src.presentation.gui.utils.translations import BRANCH_NAMES, CATEGORY_NAMES

def determine_file_branch(file_info: Dict) -> str:
    """Determine branch from file info."""
    return (
        _find_branch_from_path(file_info) or 
        _find_branch_from_filename(file_info) or 
        "other"
    )

def find_category(filename: str) -> str:
    """Find category for a filename."""
    filename = filename.lower()
    for cat_key in CATEGORY_NAMES.keys():
        is_match = (
            f"_{cat_key}" in filename or 
            filename.endswith(f"_{cat_key}.csv") or 
            filename.endswith(f"_{cat_key}.xlsx")
        )
        if is_match:
            return cat_key
    return "other"

def parse_folder_info(
    folder_name: str,
    folder_path: str, 
    prefix: str
) -> Dict:
    """Parse folder name to extract branch information."""
    parts = folder_name.replace(prefix, '').split('_')
    branch = parts[0] if parts else 'unknown'
    return {
        'name': folder_name,
        'path': folder_path,
        'branch': branch
    }

def is_branch_match(
    branch: str,
    branch_filter: Optional[str]
) -> bool:
    """Check if branch matches filter."""
    if not branch_filter or branch_filter == 'all':
        return True
    return branch == branch_filter

# Private helpers

def _find_branch_from_path(file_info: Dict) -> Optional[str]:
    """Find branch name from file path."""
    path_parts = file_info.get("relative_path", "").split(os.sep)
    for part in path_parts:
        if part in BRANCH_NAMES:
            return part
    return None

def _find_branch_from_filename(file_info: Dict) -> Optional[str]:
    """Find branch name from filename."""
    filename = file_info.get("name", "").lower()
    for key in BRANCH_NAMES.keys():
        if key in filename:
            return key
    return None
