import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the module under test
import streamlit
from src.app.gui.components.file_display import (
    render_file_expander,
    render_download_all_button
)

class TestFileDisplay:
    """Tests for file display UI components"""
    
    @patch('streamlit.expander')
    @patch('streamlit.columns')
    @patch('streamlit.download_button')
    @patch('src.app.gui.components.file_display.format_file_size', return_value="1 KB")
    @patch('src.app.gui.components.file_display.read_file_content', return_value=MagicMock())
    def test_render_file_expander(self, mock_read, mock_format, mock_download, mock_cols, mock_expander):
        """Test rendering file expander with preview"""
        file_info = {'name': 'test.csv', 'size': 1024, 'path': '/tmp/test.csv'}
        
        # Mock st.columns return value
        col1 = MagicMock()
        col2 = MagicMock()
        mock_cols.return_value = [col1, col2]
        
        # Use a context manager mock for the 'with open' part
        m_open = mock_open(read_data=b"data")
        with patch('builtins.open', m_open):
            render_file_expander(file_info, ".csv")
        
        # Verify Streamlit calls
        mock_expander.assert_called_once()
        mock_cols.assert_called_once_with([3, 1])
        mock_read.assert_called_once()
        mock_download.assert_called_once()

    @patch('streamlit.download_button')
    @patch('streamlit.markdown')
    @patch('src.app.gui.components.file_display.create_zip_archive', return_value=b"zipdata")
    def test_render_download_all_button(self, mock_zip, mock_md, mock_download):
        """Test rendering the 'Download All' button"""
        files = [{'name': 'f1.csv'}, {'name': 'f2.csv'}]
        render_download_all_button(files, "all.zip")
        
        mock_download.assert_called_once()
        args, kwargs = mock_download.call_args
        assert kwargs['file_name'] == "all.zip"
        assert kwargs['data'] == b"zipdata"

    @patch('streamlit.download_button')
    def test_render_download_all_button_empty(self, mock_download):
        """Test 'Download All' button does nothing with empty list"""
        render_download_all_button([], "empty.zip")
        mock_download.assert_not_called()
