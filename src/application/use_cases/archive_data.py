"""Use case for archiving and clearing previous output data."""

import os
from src.shared.utils.archiver import archive_all_output, clear_output_directory
from src.shared.utils.logging_utils import get_logger
from src.shared.utils.file_handler import has_files_in_directory

logger = get_logger(__name__)

class ArchiveData:
    """Manages archiving of existing output and starting fresh."""

    def __init__(self):
        self._output_directory = os.path.join("data", "output")
        self._archive_base_directory = os.path.join("data", "archive")

    def execute(self, **kwargs) -> bool:
        """Archivates previous output files if they exist."""
        try:
            if not has_files_in_directory(self._output_directory):
                logger.info("No previous output to archive. Starting fresh...")
                return True
            
            logger.info("Archiving previous output files...")
            
            archive_result = archive_all_output(
                archive_base_dir=self._archive_base_directory, 
                create_zip=True
            )
            
            # Simple summary logging
            if archive_result.get('zip_path'):
                logger.info("✓ Output archived to: %s", archive_result['zip_path'])
            
            clear_success = clear_output_directory(self._output_directory)
            if clear_success:
                logger.info("✓ Output directory cleared successfully")
            else:
                logger.warning("⚠ Some files in output directory could not be deleted")
                
            return True
        except Exception as e:
            logger.exception(f"ArchiveData use case failed: {e}")
            return False
