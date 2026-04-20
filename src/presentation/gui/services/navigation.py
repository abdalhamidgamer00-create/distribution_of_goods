"""GUI Navigation configuration."""

import streamlit as st
from src.presentation.gui.views.home_view import render_home

def get_navigation_config():
    """Returns the navigation page structure."""
    return {
        "الرئيسية": [
            st.Page("pages/00_home.py", title="Dashboard", icon="🏠", default=True)
        ],
        "🛒 قسم المشتريات": [
            st.Page("pages/01_مشتريات.py", title="إدارة الادوات", icon="⚙️"),
            st.Page("pages/06_ملفات_التحويل.py", title="ملفات التحويل", icon="📤"),
            st.Page("pages/07_الفائض_المتبقي.py", title="الفائض المتبقي", icon="📦"),
            st.Page("pages/08_النقص.py", title="تقارير النقص", icon="⚠️"),
            st.Page("pages/09_التحويلات_المجمعة_مع_نقل_الفائض_المتبقي.py", title="التحويلات المجمعة مع نقل الفائض المتبقي", icon="📋"),
            st.Page("pages/10_التحويلات_المنفصلة_مع_نقل_الفائض_المتبقي.py", title="التحويلات المنفصلة مع نقل الفائض المتبقي", icon="📂"),
            st.Page("pages/12_التحويلات_المجمعة_بدون_نقل_الفائض_المتبقي.py", title="التحويلات المجمعة بدون نقل الفائض المتبقي", icon="📦"),
        ],
        "📊 أقسام أخرى": [
            st.Page("pages/02_مبيعات.py", title="قسم المبيعات", icon="💰"),
            st.Page("pages/03_حسابات.py", title="قسم الحسابات", icon="📊"),
            st.Page("pages/04_تسويق.py", title="قسم التسويق", icon="📈"),
            st.Page("pages/05_اتش_ار.py", title="قسم اتش ار", icon="👥"),
            st.Page("pages/11_تحليل_المبيعات.py", title="تحليل المبيعات", icon="🔍"),
        ]
    }
