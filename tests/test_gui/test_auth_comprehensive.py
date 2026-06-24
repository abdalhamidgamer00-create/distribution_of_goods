"""Comprehensive tests for auth.py with Streamlit mocking.

These tests use extensive mocking to test the authentication functions
without requiring a running Streamlit environment.
"""

import sys
import hmac
from unittest.mock import patch, MagicMock, PropertyMock
from pathlib import Path

import pytest


# ===================== Fixtures =====================

@pytest.fixture
def mock_streamlit():
    """Create a comprehensive mock Streamlit module."""
    mock_st = MagicMock()
    mock_st.session_state = {}
    mock_st.secrets = {"passwords": {"admin": "admin123", "user": "user123"}}
    mock_st.warning = MagicMock()
    mock_st.error = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.text_input = MagicMock()
    mock_st.button = MagicMock(return_value=False)
    mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
    mock_st.rerun = MagicMock()
    mock_st.stop = MagicMock()
    return mock_st


@pytest.fixture
def mock_streamlit_no_secrets():
    """Create mock Streamlit without secrets."""
    mock_st = MagicMock()
    mock_st.session_state = {}
    mock_st.secrets.__getitem__ = MagicMock(side_effect=FileNotFoundError)
    mock_st.warning = MagicMock()
    return mock_st


# ===================== _get_passwords Tests =====================

class TestGetPasswords:
    """Tests for _get_passwords function."""
    
    def test_returns_secrets_when_available(self, mock_streamlit):
        """
        WHAT: Return passwords from secrets.toml
        WHY: Production should use secrets file
        BREAKS: Using defaults in production
        """
        with patch.dict('sys.modules', {'streamlit': mock_streamlit}):
            import importlib
            from src.presentation.gui.services.auth import session as auth
            importlib.reload(auth)
            
            result = auth.get_passwords()
            
            assert "admin" in result or result == {"admin": "admin123", "user": "user123"}
    
    def test_returns_empty_when_secrets_missing(self, mock_streamlit_no_secrets):
        """
        WHAT: Return empty dict when secrets not found
        WHY: App should not fall back to hardcoded passwords
        BREAKS: Hardcoded credential exposure
        """
        with patch.dict('sys.modules', {'streamlit': mock_streamlit_no_secrets}):
            import importlib
            from src.presentation.gui.services.auth import session as auth
            importlib.reload(auth)

            result = auth.get_passwords()

            assert result == {}


# ===================== _verify_credentials Tests =====================

class TestVerifyCredentials:
    """Tests for _verify_credentials function."""
    
    def test_valid_admin_credentials(self, mock_streamlit):
        """
        WHAT: Verify valid admin credentials
        WHY: Admin should be able to login
        BREAKS: Admin locked out
        """
        mock_streamlit.session_state = {"username": "admin", "password": "admin123"}
        
        with patch.dict('sys.modules', {'streamlit': mock_streamlit}):
            import importlib
            from src.presentation.gui.services.auth import session as auth
            importlib.reload(auth)
            
            result = auth.verify_credentials({"admin": "admin123", "user": "user123"})
            
            assert result is True
    
    def test_valid_user_credentials(self, mock_streamlit):
        """
        WHAT: Verify valid user credentials
        WHY: Regular user should be able to login
        BREAKS: User locked out
        """
        mock_streamlit.session_state = {"username": "user", "password": "user123"}
        
        with patch.dict('sys.modules', {'streamlit': mock_streamlit}):
            import importlib
            from src.presentation.gui.services.auth import session as auth
            importlib.reload(auth)
            
            result = auth.verify_credentials({"admin": "admin123", "user": "user123"})
            
            assert result is True
    
    def test_invalid_password(self, mock_streamlit):
        """
        WHAT: Reject invalid password
        WHY: Security - wrong passwords should fail
        BREAKS: Password bypass vulnerability
        """
        mock_streamlit.session_state = {"username": "admin", "password": "wrongpass"}
        
        with patch.dict('sys.modules', {'streamlit': mock_streamlit}):
            import importlib
            from src.presentation.gui.services.auth import session as auth
            importlib.reload(auth)
            
            result = auth.verify_credentials({"admin": "admin123"})
            
            assert result is False
    
    def test_invalid_username(self, mock_streamlit):
        """
        WHAT: Reject unknown username
        WHY: Only registered users can login
        BREAKS: Unauthorized access
        """
        mock_streamlit.session_state = {"username": "hacker", "password": "admin123"}
        
        with patch.dict('sys.modules', {'streamlit': mock_streamlit}):
            import importlib
            from src.presentation.gui.services.auth import session as auth
            importlib.reload(auth)
            
            result = auth.verify_credentials({"admin": "admin123"})
            
            assert result is False


# ===================== _handle_password_entry Tests =====================

class TestPasswordEntered:
    """Tests for _handle_password_entry function."""
    
    def test_sets_password_correct_true_on_valid(self, mock_streamlit):
        """
        WHAT: Set password_correct to True on valid credentials
        WHY: Mark user as authenticated
        BREAKS: Can't login even with correct password
        """
        mock_streamlit.session_state = {"username": "admin", "password": "admin123"}
        mock_streamlit.secrets = {"passwords": {"admin": "admin123"}}
        
        with patch.dict('sys.modules', {'streamlit': mock_streamlit}):
            import importlib
            from src.presentation.gui.services.auth import session as auth
            importlib.reload(auth)
            
            auth.handle_password_entry()
            
            assert mock_streamlit.session_state.get("password_correct") is True
    
    def test_sets_password_correct_false_on_invalid(self, mock_streamlit):
        """
        WHAT: Set password_correct to False on invalid credentials
        WHY: Mark authentication failure
        BREAKS: Invalid credentials allow access
        """
        mock_streamlit.session_state = {"username": "admin", "password": "wrongpass"}
        mock_streamlit.secrets = {"passwords": {"admin": "admin123"}}
        
        with patch.dict('sys.modules', {'streamlit': mock_streamlit}):
            import importlib
            from src.presentation.gui.services.auth import session as auth
            importlib.reload(auth)
            
            auth.handle_password_entry()
            
            assert mock_streamlit.session_state.get("password_correct") is False
    
    def test_removes_password_from_session_on_success(self, mock_streamlit):
        """
        WHAT: Remove password from session after successful login
        WHY: Security - don't keep password in memory
        BREAKS: Password exposed in session
        """
        mock_streamlit.session_state = {"username": "admin", "password": "admin123"}
        mock_streamlit.secrets = {"passwords": {"admin": "admin123"}}
        
        with patch.dict('sys.modules', {'streamlit': mock_streamlit}):
            import importlib
            from src.presentation.gui.services.auth import session as auth
            importlib.reload(auth)
            
            auth.handle_password_entry()
            
            # Password should be deleted from session
            assert "password" not in mock_streamlit.session_state


# ===================== check_password Tests =====================

class TestCheckPassword:
    """Tests for check_password main function."""
    
    def test_returns_true_when_already_logged_in(self, mock_streamlit):
        """
        WHAT: Return True if already authenticated
        WHY: Skip login form for logged-in users
        BREAKS: Login form shown every page
        """
        mock_streamlit.session_state = {"password_correct": True}
        
        with patch.dict('sys.modules', {'streamlit': mock_streamlit}):
            import importlib
            from src.presentation.gui.services.auth import session as auth
            importlib.reload(auth)
            
            result = auth.check_password_session()
            
            assert result is True
    
    def test_returns_false_when_not_logged_in(self, mock_streamlit):
        """
        WHAT: Return False when not authenticated
        WHY: Block access to protected pages
        BREAKS: Unauthorized access to app
        """
        mock_streamlit.session_state = {}
        
        with patch.dict('sys.modules', {'streamlit': mock_streamlit}):
            import importlib
            from src.presentation.gui.services.auth import session as auth
            importlib.reload(auth)
            
            result = auth.check_password_session()
            
            assert result is False


# ===================== LOGIN_STYLES Tests =====================

class TestLoginStyles:
    """Tests for LOGIN_STYLES constant."""
    
    def test_contains_rtl_direction(self):
        """
        WHAT: Verify RTL direction style
        WHY: Arabic UI needs RTL
        BREAKS: Misaligned Arabic text
        """
        from src.presentation.gui.services.auth.ui import LOGIN_STYLES
        
        assert "direction: rtl" in LOGIN_STYLES
    
    def test_is_valid_style_tag(self):
        """
        WHAT: Verify valid HTML style tag
        WHY: Streamlit needs valid HTML
        BREAKS: Styling not applied
        """
        from src.presentation.gui.services.auth.ui import LOGIN_STYLES
        
        assert "<style>" in LOGIN_STYLES
        assert "</style>" in LOGIN_STYLES


# ===================== No Hardcoded Passwords Tests =====================

class TestNoHardcodedPasswords:
    """Verify that no default passwords are embedded in source code."""

    def test_no_default_passwords_constant(self):
        """
        WHAT: DEFAULT_PASSWORDS constant must not exist
        WHY: Hardcoded credentials are a critical security risk
        BREAKS: Credentials leaked in source
        """
        from src.presentation.gui.services.auth import session as auth

        assert not hasattr(auth, "DEFAULT_PASSWORDS")
