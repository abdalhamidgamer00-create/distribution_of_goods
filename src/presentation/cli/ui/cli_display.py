"""Menu display functions"""

from src.application.pipeline.steps import AVAILABLE_STEPS
from src.presentation.cli.core.cli_constants import (
    MENU_OPTIONS,
    WELCOME_MESSAGE,
    SEPARATOR,
    ALL_STEPS_CHOICE_OFFSET,
    EXIT_CHOICE
)
from src.shared.utility.logging_utils import get_logger

logger = get_logger(__name__)


def _display_step_item(step: dict) -> None:
    """Display a single step item."""
    logger.info("  %s. %s", step["id"], step["name"])
    logger.info("     %s", step["description"])


def display_menu() -> None:
    """Display the main menu with all available steps."""
    logger.info("\n" + SEPARATOR)
    logger.info("Project Menu - Distribution of Goods")
    logger.info(SEPARATOR + "\n" + "Available steps:")
    
    for step in AVAILABLE_STEPS:
        print(f"   {step.id}. {step.name}")
        print(f"      {step.description}")
    
    msg = (
        f"\n  {ALL_STEPS_CHOICE_OFFSET}. Execute all steps\n"
        f"  {EXIT_CHOICE}. Exit\n"
        + SEPARATOR
    )
    logger.info(msg)
