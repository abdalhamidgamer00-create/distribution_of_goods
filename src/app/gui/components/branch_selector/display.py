"""Branch display components."""

import streamlit as st
from typing import Optional
from src.app.gui.components.branch_selector.constants import BRANCH_LABELS

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
