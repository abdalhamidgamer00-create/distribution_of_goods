"""Sidebar navigation component."""
import streamlit as st

def render_sidebar() -> None:
    """Render the application sidebar."""
    st.sidebar.title("💊 مشاريع صيدليات محروس")
    st.sidebar.markdown("---")
    
    st.sidebar.page_link(
        "pages/home.py", label="🏠 الرئيسية", icon="🏠"
    )
    st.sidebar.markdown("### الأقسام")
    
    _render_purchases_section()
    _render_other_sections()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### معلومات")
    _render_info_box()

def _render_purchases_section() -> None:
    """Render purchases section links."""
    with st.sidebar.expander("🛒 قسم المشتريات", expanded=False):
        st.page_link(
            "pages/purchasing_dashboard.py", label="⚙️ الادوات", icon="⚙️"
        )
        st.page_link(
            "pages/individual_transfers.py", 
            label="📤 ملفات التحويل", 
            icon="📤"
        )
        st.page_link(
            "pages/remaining_surplus.py", 
            label="📦 الفائض المتبقي", 
            icon="📦"
        )
        st.page_link(
            "pages/shortage_reports.py", 
            label="⚠️ النقص", 
            icon="⚠️"
        )
        st.page_link(
            "pages/merged_transfers_with_surplus.py", 
            label="📋 التحويلات المجمعة", 
            icon="📋"
        )
        st.page_link(
            "pages/separate_transfers_with_surplus.py", 
            label="📂 التحويلات المنفصلة", 
            icon="📂"
        )

def _render_other_sections() -> None:
    """Render other department links."""
    st.sidebar.page_link(
        "pages/sales_dashboard.py", label="💰 قسم المبيعات", icon="💰"
    )
    st.sidebar.page_link(
        "pages/accounting_dashboard.py", label="📊 قسم الحسابات", icon="📊"
    )
    st.sidebar.page_link(
        "pages/marketing_dashboard.py", label="📈 قسم التسويق", icon="📈"
    )
    st.sidebar.page_link(
        "pages/human_resources_dashboard.py", label="👥 قسم اتش ار", icon="👥"
    )

def _render_info_box() -> None:
    """Render information box."""
    informational_text = """
    **مشاريع صيدليات محروس**
    
    **الأقسام:**
    - 🛒 المشتريات
    - 💰 المبيعات
    - 📊 الحسابات
    - 📈 التسويق
    - 👥 اتش ار
    - 📊 تحليل المبيعات
    """
    st.sidebar.info(informational_text)
