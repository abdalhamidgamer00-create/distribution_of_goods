"""File and directory inspection helpers."""

import os

def has_files_in_directory(directory: str) -> bool:
    """Check if directory exists and has any files."""
    if not os.path.exists(directory):
        return False
    try:
        for root, directories, files in os.walk(directory):
            if files:
                return True
    except Exception:
        pass
    return False


def calculate_directory_size(directory: str) -> int:
    """Calculate total size of directory in bytes."""
    total_size = 0
    try:
        for directory_path, directory_names, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(directory_path, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception:
        pass
    return total_size
