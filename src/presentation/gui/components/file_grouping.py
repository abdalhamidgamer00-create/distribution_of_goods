"""File grouping and filtering helpers."""
from typing import Optional, Dict, List, Any, Tuple
from src.shared.collections import group_by


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
    return group_by(files, key_func=lambda f: f.get(branch_key, 'unknown'))


def group_files_by_source_target(
    files: List[Dict[str, Any]]
) -> Dict[Tuple[str, str], List[Dict]]:
    """Group files by source and target branches."""
    return group_by(
        files,
        key_func=lambda f: (
            f.get('source_branch', 'unknown'),
            f.get('target_branch', 'unknown'),
        ),
    )
