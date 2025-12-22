"""قسم المشتريات - نظام توزيع البضائع"""

import streamlit as st
import sys
import os

# Path configuration
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app.gui.utils.step_runner import get_all_steps
from src.app.gui.page_templates.purchases_helpers import (
    show_metrics, show_file_management, run_step_with_display,
    run_all_steps, show_nav_button, show_results_navigation
)

# Page config
st.set_page_config(page_title="قسم المشتريات", page_icon="🛒", layout="wide")

# Auth
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()

# Header
st.title("🛒 قسم المشتريات")
st.markdown("### نظام توزيع البضائع")
st.markdown("---")

# Metrics
show_metrics()
st.markdown("---")

# File management
show_file_management()
st.markdown("---")

# Steps
st.subheader("الخطوات المتاحة")
steps = get_all_steps()
visible_steps = [s for s in steps if s['id'] in ['8', '9', '10', '11']]

cols = st.columns(len(visible_steps))
for i, step in enumerate(visible_steps):
    with cols[i]:
        st.markdown(f"### {step['name']}")
        st.caption(step['description'])
        if st.button(f"▶️ تشغيل مع الخطوات السابقة", key=f"run_{step['id']}"):
            run_step_with_display(step)
        show_nav_button(step['id'])
        st.markdown("---")

# Run all
st.markdown("---")
st.subheader("تشغيل جميع الخطوات")
if st.button("🚀 تشغيل جميع الخطوات بالترتيب", type="primary", use_container_width=True):
    run_all_steps()

show_results_navigation()

# Back button
st.markdown("---")
if st.button("← العودة إلى الرئيسية"):
    st.switch_page("pages/00_الرئيسية.py")
