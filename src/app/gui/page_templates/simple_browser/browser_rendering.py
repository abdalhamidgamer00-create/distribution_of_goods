"""File list rendering logic."""

from src.app.gui.components import (
    render_file_expander,
    render_download_all_button,
)


def render_files_list(files: list, ext: str, key: str) -> None:
    """Render the list of files with download all button."""
    if not files:
        return

    # Add zip path for bulk download
    for f in files:
        f['zip_path'] = f['relative_path']
        
    render_download_all_button(files, f"{key}_{ext[1:]}.zip")
    
    for f in files:
        render_file_expander(f, ext, key_prefix=key)
