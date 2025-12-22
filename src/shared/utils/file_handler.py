"""File and directory handling"""

import os
from pathlib import Path


def ensure_directory_exists(path: str) -> None:
    """Ensure directory exists, create it if it doesn't"""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_file_path(filename: str, directory: str) -> str:
    """Get full file path"""
    return os.path.join(directory, filename)


def _collect_files_by_extension(directory: str, extensions: list) -> list:
    """Collect files matching extensions from directory."""
    if not os.path.exists(directory):
        return []
    
    files = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) and os.path.splitext(filename)[1].lower() in extensions:
            files.append(filename)
    return sorted(files)


def get_excel_files(directory: str) -> list:
    """Get list of Excel files in directory"""
    return _collect_files_by_extension(directory, ['.xlsx', '.xls'])


def get_csv_files(directory: str) -> list:
    """Get list of CSV files in directory"""
    return _collect_files_by_extension(directory, ['.csv'])


def _is_matching_file(file_path: str, filename: str, extension: str) -> bool:
    """Check if file matches criteria."""
    return os.path.isfile(file_path) and (extension is None or filename.lower().endswith(extension.lower()))


def _find_latest_in_directory(directory: str, extension: str) -> str:
    """Find the latest file by modification time in directory."""
    latest_file, latest_time = None, 0
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if _is_matching_file(file_path, filename, extension):
            mtime = os.path.getmtime(file_path)
            if mtime > latest_time:
                latest_time, latest_file = mtime, filename
    return latest_file


def get_latest_file(directory: str, extension: str = None) -> str:
    """Get latest file in directory by modification time."""
    if not os.path.exists(directory):
        return None
    return _find_latest_in_directory(directory, extension)

