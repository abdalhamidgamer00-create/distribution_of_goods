# =============================================================================
# SETUP (PATH CONFIGURATION)
# =============================================================================

import os
import sys

# Ensure project root is in sys.path for absolute imports starting with 'src'
project_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../..")
)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st

# Imports
from src.presentation.gui.services.pipeline_service import get_all_steps
from src.presentation.gui.views.purchases import (
    show_metrics,
    start_file_management_ui,
    execute_step_ui,
    run_all_steps_ui,
    render_nav_button,
    render_results_navigation
)
from src.presentation.gui.utils.auth import check_password
from src.domain.models.config import InventoryConfig

# Authentication check
if not check_password():
    st.stop()

# =============================================================================
# MAIN UI
# =============================================================================

st.title("🛒 قسم المشتريات")
st.markdown("### نظام توزيع البضائع")
st.markdown("---")

# Metrics Display
show_metrics()
st.markdown("---")

# Settings Sidebar for Coverage Criteria
with st.sidebar:
    st.markdown("### ⚙️ إعدادات التغطية")
    st.info("قم بتعديل أيام التغطية لتحديد كمية الادوية المطلوبة.")
    
    need_days = st.slider("أيام الاحتياج (Need)", 1, 240, 20)
    surplus_days = st.slider("أيام الفائض (Surplus)", 1, 240, 60)
    shortage_days = st.slider("أيام النقص (Shortage)", 1, 240, 30)
    
    inventory_configuration = InventoryConfig(
        need_days=need_days,
        surplus_days=surplus_days,
        shortage_days=shortage_days
    )
    st.markdown("---")

# File Management Section
start_file_management_ui()
st.markdown("---")

# Pipeline Step Execution Section
st.subheader("الادوات المتاحة حاليا")
pipeline_steps = get_all_steps()
visible_steps = [
    step for step in pipeline_steps 
    if step.id in ['4', '8', '9', '10', '11']
]

column_layout = st.columns(len(visible_steps))
for index, step_info in enumerate(visible_steps):
    with column_layout[index]:
        if st.button(
            f"▶️ {step_info.name}",
            key=f"run_{step_info.id}",
            use_container_width=True
        ):
            execute_step_ui(step_info, config=inventory_configuration)
            
        render_nav_button(step_info.id)
        st.markdown("---")

# Global Execution for all Tools
st.markdown("---")
st.subheader("تشغيل جميع الادوات")
if st.button(
    "🚀 تشغيل جميع الادوات بالترتيب",
    type="primary",
    use_container_width=True
):
    run_all_steps_ui(config=inventory_configuration)

# Bottom Navigation
render_results_navigation()
st.markdown("---")

if st.button("← العودة إلى الرئيسية", type="secondary"):
    st.switch_page("pages/home.py")

