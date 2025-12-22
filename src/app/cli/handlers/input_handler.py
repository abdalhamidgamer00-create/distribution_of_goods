"""User input handling functions"""

from typing import Optional
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def get_user_choice() -> str:
    """Get and return user's menu choice."""
    return input("\nSelect step number: ").strip()


def _show_file_options() -> None:
    """Display file selection options."""
    logger.info("Select file option for all steps:")
    logger.info("  1. Select specific file (will ask for each step)")
    logger.info("  2. Use latest file (applies to all steps)")


def _parse_file_choice(choice: str) -> Optional[bool]:
    """Parse user's file selection choice."""
    if choice == "1":
        return False
    elif choice == "2":
        return True
    logger.error("Invalid option!")
    return None


def get_file_selection_mode() -> Optional[bool]:
    """Get user's file selection preference for batch execution."""
    _show_file_options()
    choice = input("\nSelect option (1 or 2): ").strip()
    return _parse_file_choice(choice)

