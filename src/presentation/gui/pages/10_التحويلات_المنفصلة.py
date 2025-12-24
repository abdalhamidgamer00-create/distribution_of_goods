"""صفحة التحويلات المنفصلة."""
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
))

from src.presentation.gui.views.browsers.separate_view import (
    render_separate_browser
)
from src.presentation.gui.page_config import FILE_BROWSERS

cfg = FILE_BROWSERS['separate']
render_separate_browser(
    cfg['title'],
    cfg['icon'],
    cfg['csv'],
    cfg['excel'],
    cfg['step'],
    cfg['session_key'],
    cfg['key_prefix']
)
