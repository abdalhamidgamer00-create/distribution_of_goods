"""الصفحة الرئيسية - اختيار الأقسام"""

import streamlit as st

st.set_page_config(
    page_title="الرئيسية",
    page_icon="🏠",
    layout="wide"
)

# التحقق من تسجيل الدخول
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()

# العنوان الرئيسي
st.title("💊 مشاريع صيدليات محروس")
st.markdown("---")

# عرض الأقسام الخمسة
st.subheader("الأقسام المتاحة")

# إنشاء 5 أعمدة للأقسام
col1, col2, col3, col4, col5 = st.columns(5)

# قسم المشتريات
with col1:
    st.markdown("### 🛒 قسم المشتريات")
    st.markdown("إدارة المشتريات والطلبات")
    if st.button("الدخول إلى القسم", key="purchases", use_container_width=True):
        st.switch_page("pages/01_مشتريات.py")

# قسم المبيعات
with col2:
    st.markdown("### 💰 قسم المبيعات")
    st.markdown("إدارة المبيعات والتوزيع")
    if st.button("الدخول إلى القسم", key="sales", use_container_width=True):
        st.switch_page("pages/02_مبيعات.py")

# قسم الحسابات
with col3:
    st.markdown("### 📊 قسم الحسابات")
    st.markdown("إدارة الحسابات والمالية")
    if st.button("الدخول إلى القسم", key="accounts", use_container_width=True):
        st.switch_page("pages/03_حسابات.py")

# قسم التسويق
with col4:
    st.markdown("### 📈 قسم التسويق")
    st.markdown("إدارة التسويق والعروض")
    if st.button("الدخول إلى القسم", key="marketing", use_container_width=True):
        st.switch_page("pages/04_تسويق.py")

# قسم اتش ار
with col5:
    st.markdown("### 👥 قسم اتش ار")
    st.markdown("إدارة الموارد البشرية")
    if st.button("الدخول إلى القسم", key="hr", use_container_width=True):
        st.switch_page("pages/05_اتش_ار.py")

st.markdown("---")

# معلومات إضافية
st.info("""
**مرحباً بك في نظام مشاريع صيدليات محروس**

اختر القسم المناسب من الأقسام أعلاه للبدء في العمل.
""")
