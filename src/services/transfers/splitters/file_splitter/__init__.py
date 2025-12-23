"""File Splitter Package Facade."""

from src.services.transfers.splitters.file_splitter.processing import (
    split_transfer_file_by_type,
)
from src.services.transfers.splitters.file_splitter.orchestrator import (
    split_all_transfer_files,
)

__all__ = ['split_transfer_file_by_type', 'split_all_transfer_files']
