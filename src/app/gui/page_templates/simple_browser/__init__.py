"""Simple Browser Template Facade."""

from . import (
    browser_setup as setup,
    browser_filters as filters,
    browser_rendering as rendering
)
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
