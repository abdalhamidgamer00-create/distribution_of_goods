import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the module under test AFTER potentially mocking streamlit
import streamlit
from src.presentation.gui.components.browser_shared import (
    setup_browser_page,
    handle_branch_selection,
    render_browser_tabs
)

class TestBrowserShared:
    """Tests for shared browser UI logic"""
    
    @patch('streamlit.set_page_config')
    @patch('streamlit.title')
    @patch('streamlit.markdown')
    @patch('src.presentation.gui.utils.auth.check_password', return_value=True)
    def test_setup_browser_page_success(self, mock_auth, mock_md, mock_title, mock_config):
        """Test successful page setup"""
        result = setup_browser_page("Title", "🚀")
        
        assert result is True
        mock_config.assert_called_once()
        mock_title.assert_called_with("🚀 Title")
        
    @patch('streamlit.stop')
    @patch('streamlit.set_page_config')
    @patch('src.presentation.gui.utils.auth.check_password', return_value=False)
    def test_setup_browser_page_fail_auth(self, mock_auth, mock_config, mock_stop):
        """Test page setup failed due to authentication"""
        result = setup_browser_page("Title", "🚀")
        
        assert result is False
        mock_stop.assert_called_once()

    @patch('streamlit.subheader')
    @patch('streamlit.markdown')
    @patch('src.presentation.gui.components.browser_shared.render_branch_selection_buttons')
    @patch('src.presentation.gui.components.browser_shared.render_selected_branch_info', return_value="branch_1")
    def test_handle_branch_selection(self, mock_info, mock_buttons, mock_md, mock_subheader):
        """Test branch selection logic return value"""
        selected = handle_branch_selection("test_key")
        
        assert selected == "branch_1"
        mock_subheader.assert_called_once()
        mock_buttons.assert_called_once()

    @patch('streamlit.tabs')
    def test_render_browser_tabs(self, mock_tabs):
        """Test tab rendering and callback execution"""
        tab1 = MagicMock()
        tab2 = MagicMock()
        mock_tabs.return_value = [tab1, tab2]
        callback = MagicMock()
        
        render_browser_tabs("csv_dir", "excel_dir", callback)
        
        assert mock_tabs.called
        assert callback.call_count == 2
        # Verify first call with excel_dir and .xlsx
        callback.assert_any_call("excel_dir", ".xlsx")
        callback.assert_any_call("csv_dir", ".csv")
