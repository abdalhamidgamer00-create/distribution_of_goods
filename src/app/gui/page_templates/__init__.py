"""Page templates package."""

from src.app.gui.page_templates.file_browser import (
    build_file_info,
    list_files_in_folder,
    parse_folder_info,
    get_matching_folders,
    render_file_tabs,
    render_files_with_download
)

__all__ = [
    'build_file_info',
    'list_files_in_folder',
    'parse_folder_info',
    'get_matching_folders',
    'render_file_tabs',
    'render_files_with_download',
]
