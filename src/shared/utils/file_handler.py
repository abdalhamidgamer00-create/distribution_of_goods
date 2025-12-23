"""File and directory handling."""

import os
from pathlib import Path


# =============================================================================
# PUBLIC API
# =============================================================================

def ensure_directory_exists(path: str) -> None:
    """Ensure directory exists, create it if it doesn't."""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_file_path(filename: str, directory: str) -> str:
    """Get full file path."""
    return os.path.join(directory, filename)


def get_excel_files(directory: str) -> list:
    """Get list of Excel files in directory."""
    return _collect_files_by_extension(directory, ['.xlsx', '.xls'])


def get_csv_files(directory: str) -> list:
    """Get list of CSV files in directory."""
    return _collect_files_by_extension(directory, ['.csv'])


def get_latest_file(directory: str, extension: str = None) -> str:
    """Get latest file in directory by modification time."""
    if not os.path.exists(directory):
        return None
    return _find_latest_in_directory(directory, extension)


# =============================================================================
# FILE COLLECTION HELPERS
# =============================================================================

def _collect_files_by_extension(directory: str, extensions: list) -> list:
    """Collect files matching extensions from directory."""
    if not os.path.exists(directory):
        return []
    
    files = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if _is_file_with_extension(file_path, filename, extensions):
            files.append(filename)
    return sorted(files)


def _is_file_with_extension(path: str, name: str, extensions: list) -> bool:
    """Check if file matches extensions."""
    if not os.path.isfile(path):
        return False
    return os.path.splitext(name)[1].lower() in extensions


# =============================================================================
# LATEST FILE HELPERS
# =============================================================================

def _is_matching_file(file_path: str, filename: str, extension: str) -> bool:
    """Check if file matches criteria."""
    if not os.path.isfile(file_path):
        return False
    if extension is None:
        return True
    return filename.lower().endswith(extension.lower())


def _find_latest_in_directory(directory: str, extension: str) -> str:
    """Find the latest file by modification time in directory."""
    latest_file, latest_time = None, 0
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if _is_matching_file(file_path, filename, extension):
            modification_time = os.path.getmtime(file_path)
            if modification_time > latest_time:
                latest_time, latest_file = modification_time, filename
    return latest_file
