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
    if include_all:
        if st.button(
            all_button_label, 
            key=f"{key_prefix}_branch_btn_all", 
            use_container_width=True
        ):
            st.session_state[session_key] = 'all'
    
    _render_grid_buttons(session_key, key_prefix)


def render_selected_branch_info(
    session_key: str,
    message_template: str = "📂 عرض من: **{branch_name}**"
) -> Optional[str]:
    """Render selected branch info and return selected value."""
    if session_key not in st.session_state:
        st.warning("⚠️ يرجى اختيار فرع من الأزرار أعلاه")
        return None
        
    selected = st.session_state[session_key]
    
    if selected == 'all':
        st.info(message_template.format(
            branch_name="كل الفروع"
        ))
    else:
        st.info(message_template.format(
            branch_name=BRANCH_LABELS.get(selected, selected)
        ))
        
    return selected


def render_branch_selection_section(
    session_key: str,
    subheader_label: str,
    info_message_template: str,
    key_prefix: str = None
) -> Optional[str]:
    """Render complete branch selection section."""
    if key_prefix is None:
        key_prefix = session_key
        
    st.subheader(subheader_label)
    render_branch_selection_buttons(session_key, key_prefix)
    selected = render_selected_branch_info(session_key, info_message_template)
    st.markdown("---")
    
    return selected


# =============================================================================
# PRIVATE HELPERS
# =============================================================================

def _render_grid_buttons(session_key: str, key_prefix: str) -> None:
    """Render the grid of branch buttons."""
    branches = get_branches()
    col1, col2, col3 = st.columns(3)
    columns = [col1, col2, col3, col1, col2, col3]
    
    for idx, branch in enumerate(branches):
        with columns[idx]:
            label = BRANCH_LABELS.get(branch, branch)
            key = f"{key_prefix}_branch_btn_{branch}"
            
            if st.button(label, key=key, use_container_width=True):
                st.session_state[session_key] = branch
