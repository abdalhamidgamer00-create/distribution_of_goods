"""File path resolving helpers."""

import os
from src.shared.utils.file_handler import get_latest_file

def build_analytics_path(branch_dir: str, latest_file: str) -> str:
    """Build full path to analytics file."""
    return os.path.join(branch_dir, latest_file) if latest_file else None


def get_latest_analytics_path(analytics_dir: str, branch: str) -> str:
    """Get the path to the latest analytics file for a branch."""
    branch_dir = os.path.join(analytics_dir, branch)
    return build_analytics_path(branch_dir, get_latest_file(branch_dir, '.csv'))
