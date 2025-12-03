"""CLI interface and interactive menu - Main entry point"""

from src.app.cli.ui.display import display_menu
from src.app.cli.handlers.input_handler import get_user_choice
from src.app.cli.core.controller import handle_user_choice


def run_menu() -> None:
    """Main menu loop."""
    while True:
        display_menu()
        choice = get_user_choice()
        
        if not handle_user_choice(choice):
            break
        
        input("\nPress Enter to continue...")
