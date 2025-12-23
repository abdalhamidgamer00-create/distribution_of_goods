"""File management service integration (Facade)."""
from src.app.gui.services.file import (
    read_file_content,
    create_zip_archive,
    save_uploaded_file,
    list_output_files,
    list_files_by_mtime,
    list_files_in_folder,
    get_matching_folders,
    group_files_by_branch,
    group_files_by_category,
    group_files_by_source_target,
    collect_separate_files,
    collect_transfer_files,
    format_file_size
)

__all__ = [
    'read_file_content',
    'create_zip_archive',
    'save_uploaded_file',
    'list_output_files',
    'list_files_by_mtime',
    'list_files_in_folder',
    'get_matching_folders',
    'group_files_by_branch',
    'group_files_by_category',
    'group_files_by_source_target',
    'collect_separate_files',
    'collect_transfer_files',
    'format_file_size'
]
