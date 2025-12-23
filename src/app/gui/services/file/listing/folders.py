"""Folder matching logic."""

import os
from typing import List, Dict, Optional
from src.app.gui.services.file.classifiers import parse_folder_info, is_branch_match

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
