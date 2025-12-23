"""صفحة التحويلات المجمعة."""
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
))

from src.app.gui.views.browsers.merged_view import (
    render_merged_browser
)
from src.app.gui.page_config import FILE_BROWSERS

cfg = FILE_BROWSERS['merged']
render_merged_browser(
    cfg['title'],
    cfg['icon'],
    cfg['csv'],
    cfg['excel'],
    cfg['step'],
    cfg['session_key'],
    cfg['key_prefix']
)
