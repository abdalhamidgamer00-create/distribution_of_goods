"""Purchases view navigation component."""
import streamlit as st

NAV_BUTTON_CONFIG = {
    '8': [("📤 عرض ملفات التحويل", "pages/individual_transfers.py")],
    '9': [("📦 عرض الفائض المتبقي", "pages/remaining_surplus.py")],
    '10': [("⚠️ عرض ملفات النقص", "pages/shortage_reports.py")],
    '11': [
        ("📋 التحويلات المجمعة", "pages/merged_transfers_with_surplus.py"),
        ("📂 التحويلات المنفصلة", "pages/separate_transfers_with_surplus.py")
    ],
    '4': [("📈 عرض تحليل المبيعات", "pages/sales_data_analysis.py")]
}

NAV_BUTTONS = [
    ("📤 ملفات التحويل", "nav_all_transfer", "pages/individual_transfers.py"),
    ("📦 الفائض المتبقي", "nav_all_surplus", "pages/remaining_surplus.py"),
    ("⚠️ ملفات النقص", "nav_all_shortage", "pages/shortage_reports.py"),
    ("📋 مجمعة", "nav_all_combined", "pages/merged_transfers_with_surplus.py"),
    ("📂 منفصلة", "nav_all_separate", "pages/separate_transfers_with_surplus.py"),
    ("📈 تحليل المبيعات", "nav_all_sales", "pages/sales_data_analysis.py"),
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
    
    for index, (label, page) in enumerate(buttons):
        with cols[index]:
            if st.button(
                label, 
                key=f"nav_{step_id}_{index}", 
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
            if st.button(
                label, 
                key=key, 
                type="secondary", 
                use_container_width=True
            ):
                st.switch_page(page)
 Riverside
