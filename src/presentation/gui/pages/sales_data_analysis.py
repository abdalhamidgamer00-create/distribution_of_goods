import src.presentation.gui.page_setup  # noqa: F401  -- path bootstrap

from src.presentation.gui.page_templates.simple_browser import (
    render_simple_browser
)
from src.presentation.gui.config.file_browsers import FILE_BROWSERS

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
