"""Home dashboard view component."""

import streamlit as st

def render_home():
    """Main dashboard view."""
    st.title("💊 مشاريع صيدليات محروس")
    st.markdown("### نظام شامل لإدارة صيدليات محروس")
    st.markdown("---")
    
    st.subheader("الأقسام:")
    
    # Grid layout for departments
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    
    all_cols = [col1, col2, col3, col4, col5, col6]
    
    departments = [
        {"name": "المشتريات", "icon": "🛒", "page": "pages/01_مشتريات.py", "key": "purchases"},
        {"name": "المبيعات", "icon": "💰", "page": "pages/02_مبيعات.py", "key": "sales"},
        {"name": "الحسابات", "icon": "📊", "page": "pages/03_حسابات.py", "key": "accounts"},
        {"name": "التسويق", "icon": "📈", "page": "pages/04_تسويق.py", "key": "marketing"},
        {"name": "اتش ار", "icon": "👥", "page": "pages/05_اتش_ار.py", "key": "hr"},
        {"name": "تحليل المبيعات", "icon": "📊", "page": "pages/11_تحليل_المبيعات.py", "key": "analytics"}
    ]
    
    for col, dept in zip(all_cols, departments):
        with col:
            with st.container(border=True):
                if st.button(
                    f"{dept['icon']} {dept['name']}", 
                    key=f"home_{dept['key']}", 
                    use_container_width=True
                ):
                    st.switch_page(dept['page'])

    st.markdown("---")
