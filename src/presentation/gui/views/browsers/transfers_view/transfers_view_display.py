"""Orchestration for transfers view display logic."""
from src.presentation.gui.views.browsers.transfers_view.display import (
    display_transfer_files,
    display_collection_files,
    display_collection_files_grouped
)

# This module now serves as a clean entry point while 
# the implementation is delegated to the display/ package 
# according to the 100-line modularization rule.

