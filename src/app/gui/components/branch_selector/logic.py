"""Branch resolution logic."""

from typing import Optional
from src.app.gui.components.branch_selector.constants import BRANCH_LABELS

def get_branch_key_from_label(selected_label: str) -> Optional[str]:
    """Get branch key from selected label."""
    if selected_label == "الكل":
        return None
        
    for key, value in BRANCH_LABELS.items():
        if value == selected_label:
            return key
            
    return None
