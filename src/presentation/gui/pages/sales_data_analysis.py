# =============================================================================
# SETUP (PATH CONFIGURATION)
# =============================================================================

import os
import sys

# Ensure project root is in sys.path for absolute imports starting with 'src'
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../..")
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Imports
from src.presentation.gui.page_templates.simple_browser import (
    render_simple_browser
)
from src.presentation.gui.config.file_browsers import FILE_BROWSERS

# Main Logic using standard simple browser for analysis reports
configuration = FILE_BROWSERS['sales_analysis']
render_simple_browser(
    configuration['title'],
    configuration['icon'],
    configuration['csv'],
    configuration['excel'],
    configuration['step'],
    configuration['session_key'],
    show_branch=False,
    category='sales_analysis',
    help_text=configuration.get('help_text')
)

