"""Service for archiving and clearing previous output data."""

import os
from src.shared.utils.archiver import archive_all_output, clear_output_directory
from src.shared.utils.logging_utils import get_logger
from src.app.pipeline.step_1.cleaner.files import has_files_in_directory
from src.app.pipeline.step_1.cleaner.reporting import log_archive_summary
from src.application.interfaces.repository import DataRepository

logger = get_logger(__name__)

class ArchivatorService:
    """Manages archiving of existing output and starting fresh."""

    def __init__(self, repository: DataRepository):
        self._repository = repository
        self._output_dir = os.path.join("data", "output")
        self._archive_base_dir = os.path.join("data", "archive")

    def execute(self, **kwargs) -> bool:
        """Archivates previous output files if they exist."""
        try:
            if not has_files_in_directory(self._output_dir):
                logger.info("No previous output to archive. Starting fresh...")
                return True
            
            logger.info("Archiving previous output files...")
            
            result = archive_all_output(
                archive_base_dir=self._archive_base_dir, 
                create_zip=True
            )
            log_archive_summary(result, result['archive_dir'])
            
            clear_success = clear_output_directory(self._output_dir)
            if clear_success:
                logger.info("✓ Output directory cleared successfully")
            else:
                logger.warning("⚠ Some files could not be deleted")
                
            return True
        except Exception as e:
            logger.exception(f"ArchivatorService failed: {e}")
            return False
