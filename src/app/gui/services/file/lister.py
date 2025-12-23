"""File listing logic."""
import os
from typing import List, Dict, Optional
from .helpers import build_file_info
from .classifiers import parse_folder_info, is_branch_match

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


def list_files_by_mtime(
    directory: str,
    extensions: List[str]
) -> List[str]:
    """List filenames sorted by modification time (newest first)."""
    if not os.path.exists(directory):
        return []
        
    files = [
        f for f in os.listdir(directory) 
        if any(f.endswith(ext) for ext in extensions)
    ]
    
    return sorted(
        files, 
        key=lambda x: os.path.getmtime(os.path.join(directory, x)), 
        reverse=True
    )

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

def get_matching_folders(
    base_dir: str,
    prefix: str,
    branch_filter: Optional[str] = None
) -> List[Dict]:
    """Get all folders matching prefix and optional branch filter."""
    if not os.path.exists(base_dir):
        return []
        
    folders = []
    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        
        if not (os.path.isdir(folder_path) and 
                folder_name.startswith(prefix)):
            continue
            
        info = parse_folder_info(folder_name, folder_path, prefix)
        
        if is_branch_match(info['branch'], branch_filter):
            folders.append(info)
            
    return folders

# Private

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
