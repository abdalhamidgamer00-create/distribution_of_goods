"""Purchases view navigation component."""
import streamlit as st

NAV_BUTTON_CONFIG = {
    '8': [("📤 عرض ملفات التحويل", "pages/06_ملفات_التحويل.py")],
    '9': [("📦 عرض الفائض المتبقي", "pages/07_الفائض_المتبقي.py")],
    '10': [("⚠️ عرض ملفات النقص", "pages/08_النقص.py")],
    '11': [
        ("📋 التحويلات المجمعة", "pages/09_التحويلات_المجمعة.py"),
        ("📂 التحويلات المنفصلة", "pages/10_التحويلات_المنفصلة.py")
    ],
    '4': [("📈 عرض تحليل المبيعات", "pages/11_تحليل_المبيعات.py")]
}

NAV_BUTTONS = [
    ("📤 ملفات التحويل", "nav_all_transfer", "pages/06_ملفات_التحويل.py"),
    ("📦 الفائض المتبقي", "nav_all_surplus", "pages/07_الفائض_المتبقي.py"),
    ("⚠️ ملفات النقص", "nav_all_shortage", "pages/08_النقص.py"),
    ("📋 مجمعة", "nav_all_combined", "pages/09_التحويلات_المجمعة.py"),
    ("📂 منفصلة", "nav_all_separate", "pages/10_التحويلات_المنفصلة.py"),
    ("📈 تحليل المبيعات", "nav_all_sales", "pages/11_تحليل_المبيعات.py"),
]

def render_nav_button(step_id: str) -> None:
    """Display navigation button for specific step if successful."""
    allowed = (
        step_id in NAV_BUTTON_CONFIG and 
        st.session_state.get(f'step_{step_id}_success', False)
    )
    
    if not allowed:
        return
        
    buttons = NAV_BUTTON_CONFIG[step_id]
    cols = st.columns(len(buttons))
    
    for i, (label, page) in enumerate(buttons):
        with cols[i]:
            if st.button(
                label, 
                key=f"nav_{step_id}_{i}", 
                type="primary", 
                use_container_width=True
            ):
                st.switch_page(page)


def render_results_navigation() -> None:
    """Display navigation buttons to result pages if all steps succeeded."""
    if not st.session_state.get('all_steps_success', False):
        return
        
    st.markdown("### 📂 عرض النتائج")
    cols = st.columns(len(NAV_BUTTONS))
    
    for col, (label, key, page) in zip(cols, NAV_BUTTONS):
        with col:
            if st.button(label, key=key, use_container_width=True):
                st.switch_page(page)
