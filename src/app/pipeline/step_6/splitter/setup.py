"""Setup and validation logic for Step 6."""

import os
from src.shared.utils.file_handler import get_csv_files, ensure_directory_exists
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def ensure_branch_directories(branches: list, branches_dir: str, analytics_dir: str) -> None:
    """Ensure branch directories exist for all branches."""
    for branch in branches:
        ensure_directory_exists(os.path.join(branches_dir, branch))
        ensure_directory_exists(os.path.join(analytics_dir, branch))


def setup_and_validate(renamed_dir: str) -> tuple:
    """Setup directories and validate input files."""
    csv_files = get_csv_files(renamed_dir)
    if not csv_files:
        logger.error("No CSV files found in %s", renamed_dir)
        return None, None, None
    return csv_files, os.path.join("data", "output", "branches", "files"), os.path.join("data", "output", "branches", "analytics")
