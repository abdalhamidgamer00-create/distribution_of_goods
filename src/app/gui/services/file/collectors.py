"""File collection service for specific browser views."""
import os
import re
from typing import List, Dict, Any, Tuple
from src.app.gui.services.file.lister import list_files_in_folder, list_output_files

# =============================================================================
# SEPARATE TRANSFERS COLLECTORS
# =============================================================================

def collect_separate_files(
    sources: List[Dict[str, Any]], 
    ext: str, 
    filter_target: str, 
    filter_category: str
) -> List[Dict[str, Any]]:
    """Collect separate files matching filters from source folders."""
    files = []
    for src in sources:
        for tgt_name in os.listdir(src['path']):
            tp = os.path.join(src['path'], tgt_name)
            
            if not _is_valid_target_folder(tp, tgt_name):
                continue
                
            tgt = tgt_name.replace('to_', '')
            if filter_target and tgt != filter_target:
                continue
                
            files.extend(_get_folder_files(src, tp, tgt, tgt_name, ext, filter_category))
            
    return files


def _is_valid_target_folder(path: str, name: str) -> bool:
    """Check if folder is a valid target folder."""
    return os.path.isdir(path) and name.startswith('to_')


def _get_folder_files(
    src: Dict[str, Any], 
    tp: str, 
    tgt: str, 
    tgt_name: str, 
    ext: str, 
    filter_category: str
) -> List[Dict[str, Any]]:
    """Get files from a target folder matching criteria."""
    files = []
    for f in list_files_in_folder(tp, [ext]):
        if filter_category and filter_category not in f['name'].lower():
            continue
            
        f.update({
            'source_branch': src['branch'],
            'target_branch': tgt,
            'source_folder': src['name'],
            'target_folder': tgt_name
        })
        files.append(f)
    return files


# =============================================================================
# STANDARD TRANSFERS COLLECTORS
# =============================================================================

def collect_transfer_files(
    directory: str,
    ext: str,
    selected_branch: str,
    branches: List[str]
) -> List[Dict[str, Any]]:
    """Collect files based on selected branch for standard transfers."""
    prefix = (
        "transfers_excel_from_" if ext == ".xlsx" 
        else "transfers_from_"
    )
    files = []
    
    target_branches = branches if selected_branch == 'all' else [selected_branch]
    
    for b in target_branches:
        p = os.path.join(directory, f"{prefix}{b}_to_other_branches")
        if os.path.exists(p):
            files.extend(list_output_files(p, [ext]))
            
    return files
