"""CLI interface and interactive menu - Main entry point"""

from src.presentation.cli.ui.cli_display import display_menu
from src.presentation.cli.handlers.input_handler import get_user_choice
from src.presentation.cli.core.controller import handle_user_choice


def run_menu() -> None:
    """Main menu loop."""
    while True:
        display_menu()
        choice = get_user_choice()
        
        if not handle_user_choice(choice):
            break
        
        input("\nPress Enter to continue...")
