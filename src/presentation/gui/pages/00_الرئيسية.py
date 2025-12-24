# =============================================================================
# SETUP (PATH CONFIGURATION)
# =============================================================================

import os
import sys

# Ensure project root is in sys.path for absolute imports starting with 'src'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st

st.set_page_config(
    page_title="الرئيسية",
    page_icon="🏠",
    layout="wide"
)

# Auth
from src.presentation.gui.utils.auth import check_password
if not check_password():
    st.stop()


# =============================================================================
# MAIN UI
# =============================================================================

st.title("💊 مشاريع صيدليات محروس")
st.markdown("---")
st.subheader("الأقسام المتاحة")

col1, col2, col3, col4, col5 = st.columns(5)
columns = [col1, col2, col3, col4, col5]

departments = [
    {
        "name": "قسم المشتريات",
        "icon": "🛒", 
        "desc": "إدارة المشتريات والطلبات",
        "page": "pages/01_مشتريات.py",
        "key": "purchases"
    },
    {
        "name": "قسم المبيعات",
        "icon": "💰", 
        "desc": "إدارة المبيعات والتوزيع",
        "page": "pages/02_مبيعات.py", 
        "key": "sales"
    },
    {
        "name": "قسم الحسابات",
        "icon": "📊", 
        "desc": "إدارة الحسابات والمالية",
        "page": "pages/03_حسابات.py", 
        "key": "accounts"
    },
    {
        "name": "قسم التسويق",
        "icon": "📈", 
        "desc": "إدارة التسويق والعروض",
        "page": "pages/04_تسويق.py", 
        "key": "marketing"
    },
    {
        "name": "قسم اتش ار",
        "icon": "👥", 
        "desc": "إدارة الموارد البشرية",
        "page": "pages/05_اتش_ار.py", 
        "key": "hr"
    },
]

for col, dept in zip(columns, departments):
    with col:
        st.markdown(f"### {dept['icon']} {dept['name']}")
        st.markdown(dept['desc'])
        if st.button(
            "الدخول إلى القسم", 
            key=dept['key'], 
            use_container_width=True
        ):
            st.switch_page(dept['page'])

st.markdown("---")

st.info("""
**مرحباً بك في نظام مشاريع صيدليات محروس**

اختر القسم المناسب من الأقسام أعلاه للبدء في العمل.
""")
