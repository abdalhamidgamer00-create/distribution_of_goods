"""Public API for the transfers view display package."""
from src.presentation.gui.views.browsers.transfers_view.display.transfer_listing import (
    display_individual_transfer_files
)
from src.presentation.gui.views.browsers.transfers_view.display.collection_dashboard import (
    display_unified_collection_files
)
from src.presentation.gui.views.browsers.transfers_view.display.global_dashboard import (
    display_global_collection_dashboard
)

# Export names consistent with previous versions for backward compatibility
display_transfer_files = display_individual_transfer_files
display_collection_files = display_unified_collection_files
display_collection_files_grouped = display_global_collection_dashboard

