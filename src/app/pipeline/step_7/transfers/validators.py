"""Validation logic for transfer generation."""

import os
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def validate_analytics_directories(analytics_dir: str, branches: list) -> bool:
    """Validate that analytics directories exist for all branches."""
    for branch in branches:
        branch_dir = os.path.join(analytics_dir, branch)
        if not os.path.exists(branch_dir):
            logger.error("Analytics directory not found: %s", branch_dir)
            logger.error(
                "Please run step 5 (Split by Branches) first to generate "
                "analytics files"
            )
            return False
    return True
