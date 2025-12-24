# =============================================================================
# SETUP (PATH CONFIGURATION)
# =============================================================================

import os
import sys

# Ensure project root is in sys.path for absolute imports starting with 'src'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st

from src.presentation.gui.page_templates.simple_browser import (
    render_simple_browser
)
from src.presentation.gui.page_config import FILE_BROWSERS

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
