"""File and directory handling"""

import os
from pathlib import Path


def ensure_directory_exists(path: str) -> None:
    """Ensure directory exists, create it if it doesn't"""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_file_path(filename: str, directory: str) -> str:
    """Get full file path"""
    return os.path.join(directory, filename)


def get_excel_files(directory: str) -> list:
    """Get list of Excel files in directory"""
    excel_extensions = ['.xlsx', '.xls']
    files = []
    
    if not os.path.exists(directory):
        return files
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext in excel_extensions:
                files.append(filename)
    
    return sorted(files)


def get_csv_files(directory: str) -> list:
    """Get list of CSV files in directory"""
    files = []
    
    if not os.path.exists(directory):
        return files
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            ext = os.path.splitext(filename)[1].lower()
            if ext == '.csv':
                files.append(filename)
    
    return sorted(files)


def _find_latest_in_directory(directory: str, extension: str) -> str:
    """Find the latest file by modification time in directory."""
    latest_file = None
    latest_time = 0
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            if extension is None or filename.lower().endswith(extension.lower()):
                mtime = os.path.getmtime(file_path)
                if mtime > latest_time:
                    latest_time = mtime
                    latest_file = filename
    return latest_file


def get_latest_file(directory: str, extension: str = None) -> str:
    """Get latest file in directory by modification time."""
    if not os.path.exists(directory):
        return None
    return _find_latest_in_directory(directory, extension)

