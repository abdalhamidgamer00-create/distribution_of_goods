import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the module under test
import streamlit
from src.presentation.gui.layout.sidebar import render_sidebar

class TestSidebar:
    """Tests for sidebar layout component"""
    
    @patch('streamlit.sidebar')
    def test_render_sidebar_structure(self, mock_sidebar):
        """Test general sidebar structure and title"""
        render_sidebar()
        
        mock_sidebar.title.assert_called_with("💊 مشاريع صيدليات محروس")
        # Verify specific page links exist
        mock_sidebar.page_link.assert_any_call(
            "pages/home.py",
            label="🏠 الرئيسية",
            icon="🏠",
        )

    @patch('streamlit.sidebar')
    @patch('streamlit.page_link')
    def test_render_purchases_section(self, mock_page_link, mock_sidebar):
        """Test purchases section links within expander"""
        # Mock expander to act as a context manager
        expander_mock = MagicMock()
        mock_sidebar.expander.return_value = expander_mock
        
        render_sidebar()
        
        mock_sidebar.expander.assert_called_with("🛒 قسم المشتريات", expanded=False)
        # Check if some links were called inside the expander part (global page_link mock since st.page_link is used)
        mock_page_link.assert_any_call(
            "pages/purchasing_dashboard.py",
            label="⚙️ الادوات",
            icon="⚙️",
        )
        mock_page_link.assert_any_call(
            "pages/separate_transfers_with_surplus.py",
            label="📂 التحويلات المنفصلة",
            icon="📂",
        )

    @patch('streamlit.sidebar')
    def test_render_other_sections(self, mock_sidebar):
        """Test other department links in sidebar"""
        render_sidebar()
        
        mock_sidebar.page_link.assert_any_call(
            "pages/sales_dashboard.py",
            label="💰 قسم المبيعات",
            icon="💰",
        )
        mock_sidebar.page_link.assert_any_call(
            "pages/human_resources_dashboard.py",
            label="👥 قسم اتش ار",
            icon="👥",
        )

    @patch('streamlit.sidebar')
    def test_render_info_box(self, mock_sidebar):
        """Test info box rendering"""
        render_sidebar()
        
        mock_sidebar.info.assert_called_once()
        args, kwargs = mock_sidebar.info.call_args
        assert "مشاريع صيدليات محروس" in args[0]
