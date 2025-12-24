"""File writing logic."""
import os
import zipfile
import io
from typing import List, Dict
from .helpers import format_file_size

def create_zip_archive(
    files: List[Dict]
) -> bytes:
    """Create ZIP archive from file list."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(
        zip_buffer, 
        'w', 
        zipfile.ZIP_DEFLATED
    ) as zip_handle:
        _write_files_to_zip(zip_handle, files)
    
    zip_buffer.seek(0)
    return zip_buffer.read()

def save_uploaded_file(
    file_buffer: bytes,
    file_name: str,
    destination_dir: str
) -> str:
    """Save bytes to file."""
    os.makedirs(destination_dir, exist_ok=True)
    file_path = os.path.join(destination_dir, file_name)
    
    with open(file_path, "wb") as f:
        f.write(file_buffer)
        
    return file_path

def _write_files_to_zip(zip_handle, files: List[Dict]) -> None:
    """Write files to ZIP archive."""
    for file_info in files:
        file_path = (
            file_info.get("path") or 
            file_info.get("file_path")
        )
        
        file_name = (
            file_info.get("zip_path") or 
            file_info.get("arcname") or 
            file_info.get("name") or 
            file_info.get("file_name")
        )
        
        if file_path and os.path.exists(file_path):
            zip_handle.write(file_path, file_name)
