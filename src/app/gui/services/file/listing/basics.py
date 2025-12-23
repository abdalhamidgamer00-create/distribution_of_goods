"""Basic file listing logic."""

import os
from typing import List, Dict
from src.app.gui.services.file.helpers import build_file_info

def _collect_matching_files(
    directory: str, 
    file_extensions: List[str]
) -> List[Dict]:
    """Collect files matching extensions."""
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            _, extension = os.path.splitext(filename)
            
            if extension.lower() in file_extensions:
                file_path = os.path.join(root, filename)
                files.append(build_file_info(
                    file_path, 
                    filename, 
                    extension, 
                    directory
                ))
    return files


def list_output_files(
    directory: str, 
    file_extensions: List[str] = None
) -> List[Dict]:
    """List all files in a directory matching extensions."""
    if file_extensions is None:
        file_extensions = ['.csv', '.xlsx']
    
    if not os.path.exists(directory):
        return []
    
    matching_files = _collect_matching_files(directory, file_extensions)
    return sorted(matching_files, key=lambda f: f["name"])


def list_files_in_folder(
    folder_path: str,
    extensions: List[str]
) -> List[Dict]:
    """List files in a folder non-recursively."""
    if not os.path.exists(folder_path):
        return []
        
    return [
        build_file_info(
            os.path.join(folder_path, f), 
            f, 
            os.path.splitext(f)[1], 
            folder_path
        )
        for f in os.listdir(folder_path)
        if any(f.endswith(ext) for ext in extensions)
    ]
