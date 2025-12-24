"""File sorting logic."""

import os
from typing import List

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
