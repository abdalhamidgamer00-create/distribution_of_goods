"""Home dashboard view component."""
import streamlit as st

def render_home():
    """Main dashboard view for Mahrous Pharmacies Projects."""
    st.title("💊 مشاريع صيدليات محروس")
    st.markdown("### نظام شامل لإدارة صيدليات محروس")
    st.markdown("---")
    
    st.subheader("الأقسام:")
    
    # Grid layout for departmental dashboards
    column_1, column_2, column_3 = st.columns(3)
    column_4, column_5, column_6 = st.columns(3)
    
    all_content_columns = [
        column_1, column_2, column_3, column_4, column_5, column_6
    ]
    
    department_configurations = [
        {
            "name": "المشتريات", "icon": "🛒", 
            "page": "pages/purchasing_dashboard.py", "key": "purchases"
        },
        {
            "name": "المبيعات", "icon": "💰", 
            "page": "pages/sales_dashboard.py", "key": "sales"
        },
        {
            "name": "الحسابات", "icon": "📊", 
            "page": "pages/accounting_dashboard.py", "key": "accounts"
        },
        {
            "name": "التسويق", "icon": "📈", 
            "page": "pages/marketing_dashboard.py", "key": "marketing"
        },
        {
            "name": "اتش ار", "icon": "👥", 
            "page": "pages/human_resources_dashboard.py", "key": "hr"
        },
        {
            "name": "تحليل المبيعات", "icon": "📊", 
            "page": "pages/sales_data_analysis.py", "key": "analytics"
        }
    ]
    
    for column, department in zip(
        all_content_columns, department_configurations
    ):
        with column:
            if st.button(
                f"{department['icon']} {department['name']}", 
                key=f"home_{department['key']}", 
                use_container_width=True
            ):
                st.switch_page(department['page'])

    st.markdown("---")
