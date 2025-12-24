"""Authentication Orchestrator."""

from src.presentation.gui.services.auth.session import check_password_session
from src.presentation.gui.services.auth.ui import show_login_form

def check_password() -> bool:
    """Returns `True` if the user had a correct password."""
    if check_password_session():
        return True
    
    show_login_form()
    return False
