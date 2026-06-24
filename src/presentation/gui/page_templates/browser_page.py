"""Render a premium browser page from a FILE_BROWSERS config key.

Consolidates the repeated pattern of extracting configuration values
and calling ``render_premium_browser`` found in every browser page.
"""

from src.presentation.gui.config.file_browsers import FILE_BROWSERS
from src.presentation.gui.views.browsers.transfers_view.premium_view_layout import (
    render_premium_browser,
)


def render_browser_page(config_key: str) -> None:
    """Renders a premium browser page using the given ``FILE_BROWSERS`` key."""
    cfg = FILE_BROWSERS[config_key]
    render_premium_browser(
        cfg['title'],
        cfg['icon'],
        cfg['csv'],
        cfg['excel'],
        cfg['step'],
        cfg['session_key'],
        cfg['key_prefix'],
        cfg['category'],
        cfg.get('help_text'),
    )
