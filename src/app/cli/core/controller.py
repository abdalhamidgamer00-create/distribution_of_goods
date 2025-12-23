"""Menu control and choice handling"""

from src.app.pipeline.steps import AVAILABLE_STEPS
from src.app.cli.core.constants import EXIT_CHOICE, ALL_STEPS_CHOICE_OFFSET
from src.app.cli.executors import (
    execute_step, 
    execute_all_steps, 
    execute_step_with_dependencies
)
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def is_exit_choice(choice: str) -> bool:
    """Check if user chose to exit."""
    return choice == EXIT_CHOICE


def is_all_steps_choice(choice: str) -> bool:
    """Check if user chose to execute all steps."""
    return choice == str(ALL_STEPS_CHOICE_OFFSET)


def is_valid_step_choice(choice: str) -> bool:
    """Check if choice is a valid step ID."""
    return choice in [s.id for s in AVAILABLE_STEPS]


def _execute_choice(choice: str) -> None:
    """Execute the appropriate action based on user choice."""
    if is_all_steps_choice(choice):
        execute_all_steps()
    elif is_valid_step_choice(choice):
        execute_step_with_dependencies(choice)
    else:
        logger.error("Invalid choice! Please try again.")


def handle_user_choice(choice: str) -> bool:
    """Process user's menu choice and execute corresponding action."""
    if is_exit_choice(choice):
        logger.info("Thank you for using the program!")
        return False
    
    _execute_choice(choice)
    return True
