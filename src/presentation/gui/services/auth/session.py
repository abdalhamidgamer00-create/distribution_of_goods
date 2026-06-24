"""Authentication session logic."""

import hashlib
import hmac
import streamlit as st


def _hash_password(password: str) -> str:
    """Hash a password with SHA-256 for constant-time comparison."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_passwords() -> dict:
    """Get passwords from Streamlit secrets."""
    try:
        return dict(st.secrets["passwords"])
    except (FileNotFoundError, KeyError):
        st.error(
            "⚠️ لم يتم العثور على ملف .streamlit/secrets.toml. "
            "يرجى إنشاء الملف وتعيين بيانات الاعتماد."
        )
        return {}


def verify_credentials(passwords: dict) -> bool:
    """Verify username and password."""
    username = st.session_state.get("username", "")
    password = st.session_state.get("password", "")
    if username not in passwords:
        hmac.compare_digest(_hash_password(password), _hash_password(""))
        return False
    expected = passwords[username]
    return hmac.compare_digest(
        _hash_password(password),
        _hash_password(expected),
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
