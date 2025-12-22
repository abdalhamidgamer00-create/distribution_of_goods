"""Branch selection UI components."""

import streamlit as st
from typing import Optional

from src.core.domain.branches.config import get_branches


# =============================================================================
# CONSTANTS
# =============================================================================

BRANCH_LABELS = {
    'admin': '🏢 الإدارة',
    'asherin': '🏪 العشرين',
    'wardani': '🏬 الورداني',
    'akba': '🏭 العقبي',
    'shahid': '🏗️ الشهيد',
    'nujum': '⭐ النجوم'
}


# =============================================================================
# PUBLIC API
# =============================================================================

def get_branch_key_from_label(selected_label: str) -> Optional[str]:
    """Get branch key from selected label."""
    if selected_label == "الكل":
        return None
    for key, value in BRANCH_LABELS.items():
        if value == selected_label:
            return key
    return None


def render_branch_selection_buttons(
    session_key: str,
    key_prefix: str,
    include_all: bool = True,
    all_button_label: str = "🌐 كل الفروع"
) -> None:
    """Render branch selection buttons in a 3-column layout."""
    branches = get_branches()
    
    if include_all:
        if st.button(all_button_label, key=f"{key_prefix}_branch_btn_all", use_container_width=True):
            st.session_state[session_key] = 'all'
    
    column_1, column_2, column_3 = st.columns(3)
    columns = [column_1, column_2, column_3, column_1, column_2, column_3]
    
    for branch_index, branch in enumerate(branches):
        with columns[branch_index]:
            if st.button(BRANCH_LABELS.get(branch, branch), key=f"{key_prefix}_branch_btn_{branch}", use_container_width=True):
                st.session_state[session_key] = branch


def render_selected_branch_info(
    session_key: str,
    message_template: str = "📂 عرض من: **{branch_name}**"
) -> Optional[str]:
    """Render selected branch info and return selected value."""
    if session_key in st.session_state:
        selected = st.session_state[session_key]
        if selected == 'all':
            st.info(message_template.format(branch_name="كل الفروع"))
        else:
            st.info(message_template.format(branch_name=BRANCH_LABELS.get(selected, selected)))
        return selected
    else:
        st.warning("⚠️ يرجى اختيار فرع من الأزرار أعلاه")
        return None
