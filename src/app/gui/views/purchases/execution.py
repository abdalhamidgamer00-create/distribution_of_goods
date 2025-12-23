"""Purchases view execution component."""
import streamlit as st
from src.app.gui.services.pipeline_service import (
    run_single_step,
    get_all_steps,
    get_steps_sequence
)

def execute_step_ui(step: dict) -> None:
    """Run a step with dependencies and display result."""
    if 'selected_file' not in st.session_state:
        st.error("❌ يرجى اختيار ملف أولاً")
        return

    success, result = get_steps_sequence(step['id'])
    
    if not success:
        st.error(result)
        return
        
    all_steps = result
    _run_steps_sequence(all_steps, step)


def run_all_steps_ui() -> None:
    """Run all steps with progress UI."""
    if 'selected_file' not in st.session_state:
        st.error("❌ يرجى اختيار ملف أولاً")
        return
    
    steps = get_all_steps()
    progress = st.progress(0)
    status = st.empty()
    
    for i, step in enumerate(steps):
        status.text(f"جاري تنفيذ: {step['name']}")
        success, _ = run_single_step(step['id'])
        
        if not success:
            st.error(f"فشل في: {step['name']}")
            return
            
        progress.progress((i + 1) / len(steps))
    
    status.text("اكتمل تنفيذ جميع الخطوات!")
    st.success("✅ تم تنفيذ جميع الخطوات بنجاح!")
    st.session_state['all_steps_success'] = True


def _run_steps_sequence(all_steps: list, target_step: dict) -> None:
    """Execute a sequence of steps with progress bar."""
    progress = st.progress(0)
    status = st.empty()
    
    for i, s in enumerate(all_steps):
        status.text(f"جاري تنفيذ: {s['name']}")
        s_success, msg = run_single_step(s['id'])
        
        if not s_success:
            progress.empty()
            status.empty()
            st.error(msg)
            return
            
        progress.progress((i + 1) / len(all_steps))
        
    progress.empty()
    status.empty()
    st.success(f"✅ تم تنفيذ الخطوات حتى {target_step['name']}")
    st.session_state[f'step_{target_step["id"]}_success'] = True
