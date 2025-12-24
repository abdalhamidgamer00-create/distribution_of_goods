"""File collection logic for merged view."""

from src.presentation.gui.services.file_service import list_files_in_folder


def collect_merged_files(folders: list, ext: str) -> list:
    """Collect all files from matching folders."""
    files = []
    for fo in folders:
        for f in list_files_in_folder(fo['path'], [ext]):
            f['branch'] = fo['branch']
            f['folder_name'] = fo['name']
            files.append(f)
    return files
