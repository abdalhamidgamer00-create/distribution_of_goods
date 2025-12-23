"""File grouping logic."""
from typing import List, Dict, Tuple, Any
from .classifiers import determine_file_branch, find_category

def group_files_by_branch(
    files: List[Dict]
) -> Dict[str, List[Dict]]:
    """Group files by branch."""
    organized = {}
    
    for file_info in files:
        branch = determine_file_branch(file_info)
        
        if branch not in organized:
            organized[branch] = []
        organized[branch].append(file_info)
    
    return organized


def group_files_by_category(
    files: List[Dict]
) -> Dict[str, List[Dict]]:
    """Group files by category."""
    organized = {}
    for file_info in files:
        category = find_category(file_info["name"])
        if category not in organized:
            organized[category] = []
        organized[category].append(file_info)
    return organized


def group_files_by_source_target(
    files: List[Dict[str, Any]]
) -> Dict[Tuple[str, str], List[Dict]]:
    """Group files by source and target branches."""
    files_grouped = {}
    
    for file_info in files:
        source = file_info.get('source_branch', 'unknown')
        target = file_info.get('target_branch', 'unknown')
        key = (source, target)
        
        if key not in files_grouped:
            files_grouped[key] = []
            
        files_grouped[key].append(file_info)
        
    return files_grouped
