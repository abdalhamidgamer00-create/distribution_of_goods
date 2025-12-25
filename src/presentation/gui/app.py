import os
import sys
import streamlit as st

# =============================================================================
# SETUP (PATH CONFIGURATION)
# =============================================================================

# Ensure project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Page config (must be before any other streamlit calls)
st.set_page_config(
    page_title="مشاريع صيدليات محروس", 
    page_icon="💊", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Imports after path setup
from src.presentation.gui.layout.styles import apply_custom_styles
from src.presentation.gui.layout.sidebar import _render_info_box

# Apply premium styles early (so they affect the login page too)
apply_custom_styles()

# Auth
from src.presentation.gui.utils.auth import check_password
if not check_password():
    st.stop()

# =============================================================================
# HOME PAGE CONTENT
# =============================================================================

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

# =============================================================================
# NAVIGATION CONFIGURATION
# =============================================================================

# Define pages for st.navigation
pages = {
    "الرئيسية": [
        st.Page(render_home, title="Dashboard", icon="🏠", default=True)
    ],
    "🛒 قسم المشتريات": [
        st.Page("pages/01_مشتريات.py", title="إدارة الخطوات", icon="⚙️"),
        st.Page("pages/06_ملفات_التحويل.py", title="ملفات التحويل", icon="📤"),
        st.Page("pages/07_الفائض_المتبقي.py", title="الفائض المتبقي", icon="📦"),
        st.Page("pages/08_النقص.py", title="تقارير النقص", icon="⚠️"),
        st.Page("pages/09_التحويلات_المجمعة.py", title="التحويلات المجمعة", icon="📋"),
        st.Page("pages/10_التحويلات_المنفصلة.py", title="التحويلات المنفصلة", icon="📂"),
    ],
    "📊 أقسام أخرى": [
        st.Page("pages/02_مبيعات.py", title="قسم المبيعات", icon="💰"),
        st.Page("pages/03_حسابات.py", title="قسم الحسابات", icon="📊"),
        st.Page("pages/04_تسويق.py", title="قسم التسويق", icon="📈"),
        st.Page("pages/05_اتش_ار.py", title="قسم اتش ار", icon="👥"),
        st.Page("pages/11_تحليل_المبيعات.py", title="تحليل المبيعات", icon="🔍"),
    ]
}

# Run navigation
pg = st.navigation(pages)

# =============================================================================
# COMMON ELEMENTS (SIDEBAR)
# =============================================================================

# Standard Sidebar Branding (st.navigation handles the page links)
with st.sidebar:
    st.markdown("## 💊 صيدليات محروس")
    st.markdown("---")
    _render_info_box()

# Apply styles and run page
apply_custom_styles()
pg.run()
