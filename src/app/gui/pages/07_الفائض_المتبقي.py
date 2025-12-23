"""صفحة الفائض المتبقي."""
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
))

from src.app.gui.page_templates.simple_browser import (
    render_simple_browser
)
from src.app.gui.page_config import FILE_BROWSERS

cfg = FILE_BROWSERS['surplus']
render_simple_browser(
    cfg['title'],
    cfg['icon'],
    cfg['csv'],
    cfg['excel'],
    cfg['step'],
    cfg['session_key'],
    show_branch=True,
    category='surplus'
)
