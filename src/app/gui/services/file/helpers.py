"""Helpers for file service."""
import os
from typing import Dict

def build_file_info(
    file_path: str,
    filename: str,
    extension: str,
    directory: str
) -> Dict:
    """Build file info dictionary."""
    return {
        "name": filename,
        "path": file_path,
        "relative_path": os.path.relpath(file_path, directory),
        "size": os.path.getsize(file_path),
        "extension": extension
    }

def format_file_size(size_bytes: int) -> str:
    """Format file size to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"
