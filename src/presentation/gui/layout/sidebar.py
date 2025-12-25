"""Sidebar navigation component."""

import streamlit as st


def render_sidebar() -> None:
    """Render the application sidebar."""
    st.sidebar.title("💊 مشاريع صيدليات محروس")
    st.sidebar.markdown("---")
    
    st.sidebar.page_link(
        "pages/00_الرئيسية.py", label="🏠 الرئيسية", icon="🏠"
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
            "pages/01_مشتريات.py", label="⚙️ الخطوات", icon="⚙️"
        )
        st.page_link(
            "pages/06_ملفات_التحويل.py", 
            label="📤 ملفات التحويل", 
            icon="📤"
        )
        st.page_link(
            "pages/07_الفائض_المتبقي.py", 
            label="📦 الفائض المتبقي", 
            icon="📦"
        )
        st.page_link("pages/08_النقص.py", label="⚠️ النقص", icon="⚠️")
        st.page_link(
            "pages/09_التحويلات_المجمعة.py", 
            label="📋 التحويلات المجمعة", 
            icon="📋"
        )
        st.page_link(
            "pages/10_التحويلات_المنفصلة.py", 
            label="📂 التحويلات المنفصلة", 
            icon="📂"
        )


def _render_other_sections() -> None:
    """Render other department links."""
    st.sidebar.page_link(
        "pages/02_مبيعات.py", label="💰 قسم المبيعات", icon="💰"
    )
    st.sidebar.page_link(
        "pages/03_حسابات.py", label="📊 قسم الحسابات", icon="📊"
    )
    st.sidebar.page_link(
        "pages/04_تسويق.py", label="📈 قسم التسويق", icon="📈"
    )
    st.sidebar.page_link(
        "pages/05_اتش_ار.py", label="👥 قسم اتش ار", icon="👥"
    )


def _render_info_box() -> None:
    """Render information box."""
    info_text = """
    **مشاريع صيدليات محروس**
    
    **الأقسام:**
    - 🛒 المشتريات
    - 💰 المبيعات
    - 📊 الحسابات
    - 📈 التسويق
    - 👥 اتش ار
    - 📊 تحليل المبيعات
    """
    st.sidebar.info(info_text)
