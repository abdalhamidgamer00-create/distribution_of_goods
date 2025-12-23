"""Authentication session logic."""

import hmac
import streamlit as st

DEFAULT_PASSWORDS = {
    "admin": "admin123",
    "user": "user123"
}

def get_passwords() -> dict:
    """Get passwords from secrets or defaults."""
    try:
        return st.secrets["passwords"]
    except (FileNotFoundError, KeyError):
        msg = (
            "⚠️ استخدام كلمات المرور الافتراضية. "
            "يرجى إنشاء ملف .streamlit/secrets.toml للأمان."
        )
        st.warning(msg)
        return DEFAULT_PASSWORDS


def verify_credentials(passwords: dict) -> bool:
    """Verify username and password."""
    return (
        st.session_state["username"] in passwords and 
        hmac.compare_digest(
            st.session_state["password"],
            passwords[st.session_state["username"]]
        )
    )


def handle_password_entry() -> None:
    """Checks whether a password entered by the user is correct."""
    passwords = get_passwords()
    
    if verify_credentials(passwords):
        st.session_state["password_correct"] = True
        del st.session_state["password"]
        del st.session_state["username"]
    else:
        st.session_state["password_correct"] = False


def check_password_session() -> bool:
    """
    Returns `True` if the user had a correct password (session check only).
    """
    return st.session_state.get("password_correct", False)


def logout():
    """Log out the user."""
    st.session_state["password_correct"] = False
    st.rerun()
