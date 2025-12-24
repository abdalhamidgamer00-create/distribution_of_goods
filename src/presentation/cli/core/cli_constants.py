"""Constants for CLI menu"""

from src.application.pipeline.steps import AVAILABLE_STEPS

SEPARATOR = "=" * 50
EXIT_CHOICE = "0"
ALL_STEPS_CHOICE_OFFSET = len(AVAILABLE_STEPS) + 1

WELCOME_MESSAGE = f"""
{SEPARATOR}
   Distribution System - CLI Menu
{SEPARATOR}
"""

MENU_OPTIONS = [
    (str(i + 1), step.name) for i, step in enumerate(AVAILABLE_STEPS)
]
MENU_OPTIONS.append((str(ALL_STEPS_CHOICE_OFFSET), "Run All Steps"))
MENU_OPTIONS.append((EXIT_CHOICE, "Exit"))
