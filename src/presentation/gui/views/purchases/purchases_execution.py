"""Purchases view execution component."""
import streamlit as st
from typing import Any
from src.presentation.gui.services.pipeline_service import (
    run_single_step,
    get_all_steps,
    get_steps_sequence,
    get_step_info
)

def execute_step_ui(step: Any) -> None:
    """Run archiving followed by the target step using centralized orchestrator."""
    if 'selected_file' not in st.session_state:
        st.error("❌ يرجى اختيار ملف أولاً")
        return
    
    from src.application.pipeline.step_orchestrator import StepOrchestrator
    steps_to_run = StepOrchestrator.get_isolated_sequence(step.id)
    
    if not steps_to_run:
        st.error(f"❌ لم يتم العثور على الخطوة: {step.id}")
        return

    _run_steps_sequence(steps_to_run, step)


def run_all_steps_ui() -> None:
    """Run all steps with progress UI."""
    if 'selected_file' not in st.session_state:
        st.error("❌ يرجى اختيار ملف أولاً")
        return
    
    steps = get_all_steps()
    progress = st.progress(0)
    status = st.empty()
    
    for i, step in enumerate(steps):
        status.text(f"جاري تنفيذ: {step.name}")
        success, _ = run_single_step(step.id)
        
        if not success:
            st.error(f"فشل في: {step.name}")
            return
            
        progress.progress((i + 1) / len(steps))
    
    status.text("اكتمل تنفيذ جميع الادوات!")
    st.success("✅ تم تنفيذ جميع الادوات بنجاح!")
    st.session_state['all_steps_success'] = True


def _run_steps_sequence(all_steps: list, target_step: Any) -> None:
    """Execute a sequence of steps with progress bar."""
    progress = st.progress(0)
    status = st.empty()
    
    for i, s in enumerate(all_steps):
        status.text(f"جاري تنفيذ: {s.name}")
        s_success, msg = run_single_step(s.id)
        
        if not s_success:
            progress.empty()
            status.empty()
            st.error(msg)
            return
            
        progress.progress((i + 1) / len(all_steps))
        
    progress.empty()
    status.empty()
    
    if len(all_steps) == 1:
        st.success(f"✅ تم تنفيذ {target_step.name} بنجاح")
    elif len(all_steps) == 2 and all_steps[0].id == "1":
        st.success(f"✅ تم الأرشفة وتنفيذ {target_step.name} بنجاح")
    else:
        st.success(f"✅ تم تنفيذ الادوات حتى {target_step.name}")
        
    st.session_state[f'step_{target_step.id}_success'] = True
