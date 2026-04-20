"""Orchestration for transfers view display logic."""
from src.presentation.gui.views.browsers.transfers_view.display import (
    display_transfer_files,
    display_collection_files,
    display_collection_files_grouped
)

# Aliases for backward compatibility with previous logic versions
display_transfer_files_grouped = display_collection_files_grouped
