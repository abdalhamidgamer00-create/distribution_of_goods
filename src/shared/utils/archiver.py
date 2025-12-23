"""Archive output files.

This module is a backward-compatible facade for the new archiver package.
"""

from src.shared.utils.archiver import (
    archive_output_directory,
    create_zip_archive,
    archive_all_output,
    clear_output_directory,
)
