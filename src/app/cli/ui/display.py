"""Menu display functions"""

from src.app.pipeline.steps import AVAILABLE_STEPS
from src.app.cli.core.constants import SEPARATOR, EXIT_CHOICE, ALL_STEPS_CHOICE_OFFSET
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def display_menu() -> None:
    """Display the main menu with all available steps."""
    logger.info("\n" + SEPARATOR)
    logger.info("Project Menu - Distribution of Goods")
    logger.info(SEPARATOR)
    logger.info("\nAvailable steps:")
    
    for step in AVAILABLE_STEPS:
        logger.info("  %s. %s", step["id"], step["name"])
        logger.info("     %s", step["description"])
    
    logger.info("\n  %s. Execute all steps", ALL_STEPS_CHOICE_OFFSET)
    logger.info("  %s. Exit", EXIT_CHOICE)
    logger.info(SEPARATOR)

