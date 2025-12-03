"""User input handling functions"""

from typing import Optional
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def get_user_choice() -> str:
    """Get and return user's menu choice."""
    return input("\nSelect step number: ").strip()


def get_file_selection_mode() -> Optional[bool]:
    """
    Get user's file selection preference for batch execution.
    
    Returns:
        True if use latest file, False if select specific, None if invalid
    """
    logger.info("Select file option for all steps:")
    logger.info("  1. Select specific file (will ask for each step)")
    logger.info("  2. Use latest file (applies to all steps)")
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice == "1":
        return False
    elif choice == "2":
        return True
    else:
        logger.error("Invalid option!")
        return None

