"""GUI Navigation configuration."""

import streamlit as st

def get_navigation_config():
    """Returns the navigation page structure."""
    return {
        "الرئيسية": [
            st.Page(
                "pages/home.py", 
                title="Dashboard", 
                icon="🏠", 
                default=True
            )
        ],
        "🛒 قسم المشتريات": [
            st.Page(
                "pages/purchasing_dashboard.py", 
                title="إدارة الادوات", 
                icon="⚙️"
            ),
            st.Page(
                "pages/transfer_ratio.py",
                title="نسبة التحويل",
                icon="📊"
            ),
            st.Page(
                "pages/individual_transfers.py", 
                title="ملفات التحويل", 
                icon="📤"
            ),
            st.Page(
                "pages/remaining_surplus.py", 
                title="الفائض المتبقي", 
                icon="📦"
            ),
            st.Page(
                "pages/shortage_reports.py", 
                title="تقارير النقص", 
                icon="⚠️"
            ),
            st.Page(
                "pages/merged_transfers_with_surplus.py", 
                title="التحويلات المجمعة مع نقل الفائض المتبقي", 
                icon="📋"
            ),
            st.Page(
                "pages/separate_transfers_with_surplus.py", 
                title="التحويلات المنفصلة مع نقل الفائض المتبقي", 
                icon="📂"
            ),
            st.Page(
                "pages/aggregated_collections.py", 
                title="التحويلات المجمعة بدون نقل الفائض المتبقي", 
                icon="📦"
            ),
        ],
        "📊 أقسام أخرى": [
            st.Page(
                "pages/sales_dashboard.py", 
                title="قسم المبيعات", 
                icon="💰"
            ),
            st.Page(
                "pages/accounting_dashboard.py", 
                title="قسم الحسابات", 
                icon="📊"
            ),
            st.Page(
                "pages/marketing_dashboard.py", 
                title="قسم التسويق", 
                icon="📈"
            ),
            st.Page(
                "pages/human_resources_dashboard.py", 
                title="قسم اتش ار", 
                icon="👥"
            ),
            st.Page(
                "pages/sales_data_analysis.py", 
                title="تحليل المبيعات", 
                icon="🔍"
            ),
        ]
    }
