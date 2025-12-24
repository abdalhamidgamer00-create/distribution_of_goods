"""صفحة ملفات التحويل."""
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
))

from src.presentation.gui.views.browsers.transfers_view import (
    render_transfers_browser
)
from src.presentation.gui.page_config import FILE_BROWSERS

cfg = FILE_BROWSERS['transfers']
render_transfers_browser(
    cfg['title'],
    cfg['icon'],
    cfg['csv'],
    cfg['excel'],
    cfg['step'],
    cfg['session_key'],
    cfg['key_prefix']
)
