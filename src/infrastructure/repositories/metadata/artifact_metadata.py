"""Logic for creating and enriching artifact metadata."""

import os
from typing import Dict


def create_artifact_metadata(
    name: str, 
    path: str, 
    category: str, 
    branch: str, 
    folder: str,
    root_dir: str = ""
) -> Dict:
    """Creates the base metadata dictionary with relative path support."""
    abspath = os.path.abspath(path)
    metadata = {
        'name': name,
        'path': abspath,
        'size': os.path.getsize(path),
        'mtime': os.path.getmtime(path),
        'category': category,
        'branch': branch,
        'folder_name': folder
    }
    
    if root_dir:
        abs_root = os.path.abspath(root_dir)
        metadata['relative_path'] = os.path.relpath(abspath, abs_root)
    else:
        metadata['relative_path'] = name
        
    return metadata


def enrich_separate_metadata(
    metadata: Dict, 
    search_dir: str, 
    item: str, 
    folder: str
) -> None:
    """Enriches metadata for the 'separate' category of transfers."""
    metadata['source_folder'] = os.path.basename(os.path.dirname(search_dir))
    metadata['target_folder'] = folder
    
    stem = item.split('.')[0]
    if '_to_' in stem:
        _extract_branch_category(metadata, stem)


def _extract_branch_category(metadata: Dict, stem: str) -> None:
    """Extracts target branch and product category from file stem."""
    parts = stem.split('_')
    try:
        to_index = parts.index('to')
        metadata['target_branch'] = parts[to_index + 1]
        metadata['product_category'] = parts[to_index + 2]
    except (ValueError, IndexError):
        pass
