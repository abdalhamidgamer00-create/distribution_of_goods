"""تطبيق Streamlit الرئيسي"""

import streamlit as st
import os
import sys

# Fix import path for Streamlit Cloud
if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# إعداد الصفحة
st.set_page_config(
    page_title="مشاريع صيدليات محروس",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# التحقق من تسجيل الدخول
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()

# CSS مخصص للعربية
st.markdown("""
<style>
    .main {
        direction: rtl;
        text-align: right;
    }
    .stButton>button {
        width: 100%;
    }
    h1, h2, h3 {
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# القائمة الجانبية
st.sidebar.title("💊 مشاريع صيدليات محروس")
st.sidebar.markdown("---")

# روابط الصفحات الرئيسية
st.sidebar.page_link("pages/00_الرئيسية.py", label="🏠 الرئيسية", icon="🏠")
st.sidebar.markdown("### الأقسام")

# قسم المشتريات مع قائمة منسدلة للصفحات الفرعية
with st.sidebar.expander("🛒 قسم المشتريات", expanded=False):
    st.page_link("pages/01_مشتريات.py", label="⚙️ الخطوات", icon="⚙️")
    st.page_link("pages/06_ملفات_التحويل.py", label="📤 ملفات التحويل", icon="📤")
    st.page_link("pages/07_الفائض_المتبقي.py", label="📦 الفائض المتبقي", icon="📦")
    st.page_link("pages/08_النقص.py", label="⚠️ النقص", icon="⚠️")


st.sidebar.page_link("pages/02_مبيعات.py", label="💰 قسم المبيعات", icon="💰")
st.sidebar.page_link("pages/03_حسابات.py", label="📊 قسم الحسابات", icon="📊")
st.sidebar.page_link("pages/04_تسويق.py", label="📈 قسم التسويق", icon="📈")
st.sidebar.page_link("pages/05_اتش_ار.py", label="👥 قسم اتش ار", icon="👥")

st.sidebar.markdown("---")
st.sidebar.markdown("### معلومات")
st.sidebar.info("""
**مشاريع صيدليات محروس**

نظام شامل لإدارة صيدليات محروس

**الأقسام:**
- 🛒 المشتريات
- 💰 المبيعات
- 📊 الحسابات
- 📈 التسويق
- 👥 اتش ار
""")

# المحتوى الرئيسي (سيتم عرضه من الصفحات)
if "page" not in st.session_state:
    st.session_state.page = "home"

