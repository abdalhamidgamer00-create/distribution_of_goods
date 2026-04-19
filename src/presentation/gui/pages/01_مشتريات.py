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


# Auth
from src.presentation.gui.utils.auth import check_password
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

# Settings Sidebar
from src.domain.models.config import InventoryConfig

with st.sidebar:
    st.markdown("### ⚙️ إعدادات التغطية", help="تعديل معايير حساب الاحتياج والفائض لضبط مخرجات النظام.")
    st.info("قم بتعديل أيام التغطية لتحديد كمية الادوية التي سوف تتحرك بين الفروع او تطلب من الخارج")
    
    need_days = st.slider(
        "أيام الاحتياج (Need)", 1, 240, 20,
        help="الفترة التي نحتاج لتغطيتها بالفروع لضمان عدم حدوث عجز (الطلب المثالي)."
    )
    surplus_days = st.slider(
        "أيام الفائض (Surplus)", 1, 240, 60,
        help="الحد الأقصى للتخزين؛ أي كمية تتجاوز هذه الأيام تعتبر فائضاً يجب نقله."
    )
    shortage_days = st.slider(
        "أيام النقص (Shortage)", 1, 240, 30,
        help="الحد الأدنى للتغطية؛ إذا قل المخزون عن هذه الأيام يظهر المنتج في تقرير النواقص للطلب من الخارج."
    )
    
    config = InventoryConfig(
        need_days=need_days,
        surplus_days=surplus_days,
        shortage_days=shortage_days
    )
    st.markdown("---")

# File management
start_file_management_ui()
st.markdown("---")

# Steps
st.subheader("الادوات المتاحة حاليا")
steps = get_all_steps()
visible_steps = [s for s in steps if s.id in ['4', '8', '9', '10', '11']]

cols = st.columns(len(visible_steps))
for i, step in enumerate(visible_steps):
    with cols[i]:
        if st.button(
            f"▶️ {step.name}",
            key=f"run_{step.id}",
            use_container_width=True
        ):
            execute_step_ui(step, config=config)
            
        render_nav_button(step.id)
        st.markdown("---")

# Run all
st.markdown("---")
st.subheader("تشغيل جميع الادوات")
if st.button(
    "🚀 تشغيل جميع الادوات بالترتيب",
    type="primary",
    use_container_width=True
):
    run_all_steps_ui(config=config)

render_results_navigation()

st.markdown("---")
if st.button("← العودة إلى الرئيسية", type="secondary"):
    st.switch_page("pages/00_home.py")
