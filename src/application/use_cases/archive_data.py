"""Use case for archiving and clearing previous output data."""

from src.shared.utils.archiver import archive_all_output, clear_output_directory
from src.shared.utils.logging_utils import get_logger
from src.shared.utils.file_handler import has_files_in_directory
from src.shared.config.paths import OUTPUT_DIR, ARCHIVE_DIR

logger = get_logger(__name__)


class ArchiveData:
    """Manages archiving of existing output and starting fresh."""

    def __init__(self):
        self._output_directory = OUTPUT_DIR
        self._archive_base_directory = ARCHIVE_DIR

    def execute(self, **kwargs) -> bool:
        """Archivates previous output files if they exist."""
        try:
            if not has_files_in_directory(self._output_directory):
                logger.info("No previous output to archive. Starting fresh...")
                return True
            
            return self._perform_archiving_and_cleanup()
        except Exception as error:
            logger.exception(f"ArchiveData use case failed: {error}")
            return False

    def _perform_archiving_and_cleanup(self) -> bool:
        """Handles the sequence of archiving data and clearing the output."""
        logger.info("Archiving previous output files...")
        
        archive_result = archive_all_output(
            archive_base_dir=self._archive_base_directory, 
            create_zip=True
        )
        
        if archive_result.get('zip_path'):
            logger.info("✓ Output archived to: %s", archive_result['zip_path'])
        
        return self._clear_output_safely()

    def _clear_output_safely(self) -> bool:
        """Clears the output directory and logs any issues."""
        clear_success = clear_output_directory(self._output_directory)
        if clear_success:
            logger.info("✓ Output directory cleared successfully")
        else:
            logger.warning("⚠ Some files in output directory could not be deleted")
        return True
