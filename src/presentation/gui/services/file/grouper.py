"""File grouping logic."""
from typing import List, Dict, Tuple, Any
from .classifiers import determine_file_branch, find_category
from src.shared.collections import group_by


def group_files_by_branch(
    files: List[Dict]
) -> Dict[str, List[Dict]]:
    """Group files by branch."""
    return group_by(files, key_func=determine_file_branch)


def group_files_by_category(
    files: List[Dict]
) -> Dict[str, List[Dict]]:
    """Group files by category."""
    return group_by(files, key_func=lambda f: find_category(f["name"]))


def group_files_by_source_target(
    files: List[Dict[str, Any]]
) -> Dict[Tuple[str, str], List[Dict]]:
    """Group files by source and target branches."""
    return group_by(
        files,
        key_func=lambda f: (
            f.get('source_branch', 'unknown'),
            f.get('target_branch', 'unknown'),
        ),
    )
