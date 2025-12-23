"""File grouping and filtering helpers."""
from typing import Optional, Dict, List, Any, Tuple


# =============================================================================
# PUBLIC API
# =============================================================================

def get_key_from_label(
    label: str, 
    labels_dict: Dict[str, str]
) -> Optional[str]:
    """Get key from translated label."""
    if label == "الكل":
        return None
        
    for key, value in labels_dict.items():
        if value == label:
            return key
            
    return None


def group_files_by_branch(
    files: List[Dict[str, Any]], 
    branch_key: str = 'branch'
) -> Dict[str, List[Dict]]:
    """Group files by branch."""
    files_by_branch = {}
    
    for file_info in files:
        branch = file_info.get(branch_key, 'unknown')
        
        if branch not in files_by_branch:
            files_by_branch[branch] = []
            
        files_by_branch[branch].append(file_info)
        
    return files_by_branch


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
