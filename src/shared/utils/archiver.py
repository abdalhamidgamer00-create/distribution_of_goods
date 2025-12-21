"""Archive output files"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from src.shared.utils.logging_utils import get_logger

logger = get_logger(__name__)


def _count_directory_contents(directory: str) -> tuple:
    """Count files and directories in a path."""
    file_count = 0
    dir_count = 0
    for root, dirs, files in os.walk(directory):
        dir_count += len(dirs)
        file_count += len(files)
    return file_count, dir_count


def _copy_directory_tree(source: str, destination: str) -> None:
    """Copy complete directory tree, removing destination if exists."""
    if os.path.exists(destination):
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def archive_output_directory(output_dir: str, archive_base_dir: str = "data/archive") -> dict:
    """
    Archive ALL files and directories from output directory to a timestamped archive.
    
    Returns:
        Dictionary with archive information including file and directory counts
    """
    if not os.path.exists(output_dir):
        raise ValueError(f"Output directory not found: {output_dir}")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = os.path.join(archive_base_dir, f"archive_{timestamp}")
    
    os.makedirs(archive_base_dir, exist_ok=True)
    os.makedirs(archive_dir, exist_ok=True)
    
    output_name = os.path.basename(output_dir.rstrip('/'))
    archive_output_dir = os.path.join(archive_dir, output_name)
    
    logger.info("Archiving complete contents of %s...", output_dir)
    logger.info("  Source: %s", output_dir)
    logger.info("  Destination: %s", archive_output_dir)
    
    file_count, dir_count = _count_directory_contents(output_dir)
    logger.info("  Found %s files in %s directories", file_count, dir_count)
    
    if os.path.exists(output_dir):
        _copy_directory_tree(output_dir, archive_output_dir)
    
    archived_file_count, archived_dir_count = _count_directory_contents(archive_output_dir)
    
    logger.info("Archive created successfully!")
    logger.info("  - Archive location: %s", archive_dir)
    logger.info("  - Archived %s files in %s directories", archived_file_count, archived_dir_count)
    
    return {
        'archive_dir': archive_dir,
        'file_count': archived_file_count,
        'dir_count': archived_dir_count
    }



def create_zip_archive(archive_dir: str, zip_output_path: str = None) -> str:
    """
    Create a ZIP file from archive directory
    
    Args:
        archive_dir: Directory to compress
        zip_output_path: Optional path for ZIP file (default: archive_dir + .zip)
        
    Returns:
        Path to the created ZIP file
    """
    import zipfile
    
    if not os.path.exists(archive_dir):
        raise ValueError(f"Archive directory not found: {archive_dir}")
    
    if zip_output_path is None:
        zip_output_path = f"{archive_dir}.zip"
    
    logger.info("Creating ZIP archive: %s...", zip_output_path)
    
    with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(archive_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, archive_dir)
                zipf.write(file_path, arcname)
    
    logger.info("ZIP archive created successfully: %s", zip_output_path)
    
    return zip_output_path


def archive_all_output(archive_base_dir: str = "data/archive", create_zip: bool = True) -> dict:
    """
    Archive ALL contents of the output directory
    
    This function archives the complete output directory including:
    - All subdirectories: analytics, branches, converted, renamed, transfers, transfers_excel
    - All files in all subdirectories
    - Complete directory structure is preserved
    
    Args:
        archive_base_dir: Base directory for archives
        create_zip: Whether to create a ZIP file as well
        
    Returns:
        Dictionary with archive information including file counts
    """
    output_dir = "data/output"
    
    if not os.path.exists(output_dir):
        raise ValueError(f"Output directory not found: {output_dir}")
    
    # Create archive directory (returns dict with file/dir counts)
    archive_info = archive_output_directory(output_dir, archive_base_dir)
    archive_dir = archive_info['archive_dir']
    
    result = {
        'archive_dir': archive_dir,
        'file_count': archive_info.get('file_count', 0),
        'dir_count': archive_info.get('dir_count', 0),
        'zip_file': None
    }
    
    # Create ZIP if requested
    if create_zip:
        zip_file = create_zip_archive(archive_dir)
        result['zip_file'] = zip_file
    
    return result


def _delete_directory_contents(directory: str) -> None:
    """Delete all contents of a directory but keep the directory itself."""
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        try:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        except Exception as e:
            logger.warning("  Warning: Could not delete %s: %s", item_path, e)


def clear_output_directory(output_dir: str = "data/output") -> bool:
    """
    Clear all contents of the output directory after archiving.
    
    Returns:
        True if successful, False otherwise
    """
    if not os.path.exists(output_dir):
        logger.warning("Output directory not found: %s", output_dir)
        return True
    
    try:
        logger.info("Clearing output directory: %s...", output_dir)
        
        file_count, dir_count = _count_directory_contents(output_dir)
        
        if file_count == 0 and dir_count == 0:
            logger.info("  Output directory is already empty.")
            return True
        
        logger.info("  Found %s files in %s directories to delete", file_count, dir_count)
        
        _delete_directory_contents(output_dir)
        
        remaining_files, remaining_dirs = _count_directory_contents(output_dir)
        
        if remaining_files == 0 and remaining_dirs == 0:
            logger.info("  ✓ Output directory cleared successfully!")
            logger.info("  ✓ Deleted %s files and %s directories", file_count, dir_count)
            return True
        else:
            logger.warning("  ⚠ Some files/directories could not be deleted")
            logger.warning("  Remaining: %s files, %s directories", remaining_files, remaining_dirs)
            return False
            
    except Exception as e:
        logger.exception("  ✗ Error clearing output directory: %s", e)
        return False


