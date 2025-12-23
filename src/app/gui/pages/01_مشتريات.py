"""قسم المشتريات - نظام توزيع البضائع."""
import streamlit as st
import sys
import os

# =============================================================================
# SETUP
# =============================================================================

# Path configuration
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Imports
from src.app.gui.services.pipeline_service import get_all_steps
from src.app.gui.views.purchases_view import (
    show_metrics,
    start_file_management_ui,
    execute_step_ui,
    run_all_steps_ui,
    render_nav_button,
    render_results_navigation
)

# Page config
st.set_page_config(
    page_title="قسم المشتريات",
    page_icon="🛒",
    layout="wide"
)

# Auth
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()


# =============================================================================
# MAIN UI
# =============================================================================

st.title("🛒 قسم المشتريات")
st.markdown("### نظام توزيع البضائع")
st.markdown("---")

# Metrics
show_metrics()
st.markdown("---")

# File management
start_file_management_ui()
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
        
        if st.button(
            f"▶️ تشغيل مع الخطوات السابقة",
            key=f"run_{step['id']}"
        ):
            execute_step_ui(step)
            
        render_nav_button(step['id'])
        st.markdown("---")

# Run all
st.markdown("---")
st.subheader("تشغيل جميع الخطوات")
if st.button(
    "🚀 تشغيل جميع الخطوات بالترتيب",
    type="primary",
    use_container_width=True
):
    run_all_steps_ui()

render_results_navigation()

# Back button
st.markdown("---")
if st.button("← العودة إلى الرئيسية"):
    st.switch_page("pages/00_الرئيسية.py")
