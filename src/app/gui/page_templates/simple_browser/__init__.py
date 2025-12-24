"""Simple Browser Template Facade."""

from src.app.gui.page_templates.simple_browser import browser_setup as setup
from src.app.gui.page_templates.simple_browser import browser_filters as filters
from src.app.gui.page_templates.simple_browser import browser_rendering as rendering
from src.app.gui.page_templates.simple_browser.browser_layout import (
    render_simple_browser
)
from src.app.gui.components import setup_browser_page

__all__ = [
    'render_simple_browser', 
    'setup_browser_page',
    'setup',
    'filters',
    'rendering'
]
