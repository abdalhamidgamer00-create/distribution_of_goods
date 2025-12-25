"""Home dashboard view component."""

import streamlit as st

def render_home():
    """Main dashboard view."""
    st.title("💊 مشاريع صيدليات محروس")
    st.markdown("<h3 style='text-align: right;'>نظام إدارة وتوزيع البضائع الذكي</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("🏢 الأقسام والعمليات")
    
    # Grid layout for departments
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)
    
    all_cols = [col1, col2, col3, col4, col5, col6]
    
    departments = [
        {
            "name": "قسم المشتريات",
            "icon": "🛒", 
            "desc": "إدارة توزيع الطلبيات والمزودين",
            "page": "pages/01_مشتريات.py",
            "key": "purchases"
        },
        {
            "name": "قسم المبيعات",
            "icon": "💰", 
            "desc": "متابعة أداء المبيعات اليومي",
            "page": "pages/02_مبيعات.py", 
            "key": "sales"
        },
        {
            "name": "قسم الحسابات",
            "icon": "📊", 
            "desc": "التقارير المالية والمطالبات",
            "page": "pages/03_حسابات.py", 
            "key": "accounts"
        },
        {
            "name": "قسم التسويق",
            "icon": "📈", 
            "desc": "إدارة العروض والحملات",
            "page": "pages/04_تسويق.py", 
            "key": "marketing"
        },
        {
            "name": "قسم اتش ار",
            "icon": "👥", 
            "desc": "شؤون الموظفين والدوام",
            "page": "pages/05_اتش_ار.py", 
            "key": "hr"
        },
        {
            "name": "تحليل المبيعات",
            "icon": "📊", 
            "desc": "تحليلات متقدمة والذكاء الاصطناعي",
            "page": "pages/11_تحليل_المبيعات.py", 
            "key": "analytics"
        }
    ]
    
    for col, dept in zip(all_cols, departments):
        with col:
            with st.container(border=True):
                st.markdown(f"### {dept['icon']} {dept['name']}")
                st.write(dept['desc'])
                if st.button(
                    "دخول القسم", 
                    key=f"home_{dept['key']}", 
                    use_container_width=True
                ):
                    st.switch_page(dept['page'])

    st.markdown("---")
    
    st.info("""
    **✅ حالة النظام**: البرنامج يعمل بكفاءة. 
    يرجى اختيار القسم المناسب من القائمة الجانبية أو من البطاقات أعلاه للبدء.
    """)
