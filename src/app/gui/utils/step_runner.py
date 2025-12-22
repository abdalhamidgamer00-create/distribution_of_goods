"""تشغيل خطوات المعالجة من واجهة Streamlit"""

from src.app.pipeline.steps import AVAILABLE_STEPS
from src.app.gui.utils.translations import STEP_NAMES, STEP_DESCRIPTIONS, MESSAGES
import traceback


def _find_step_by_id(step_id: str):
    """Find step by its ID."""
    for s in AVAILABLE_STEPS:
        if s["id"] == step_id:
            return s
    return None


def _execute_step_function(step, step_name: str, use_streamlit: bool) -> tuple:
    """Execute step function with optional Streamlit spinner."""
    if use_streamlit:
        import streamlit as st
        with st.spinner(f"{MESSAGES['running']} {step_name}..."):
            result = step["function"](use_latest_file=True)
    else:
        result = step["function"](use_latest_file=True)
    
    if result:
        return True, f"{MESSAGES['success']}: {step_name}"
    return False, f"{MESSAGES['failed']}: {step_name}"


def _handle_run_step_error(step_name: str, error: Exception, use_streamlit: bool) -> tuple:
    """Handle step execution error."""
    error_msg = f"{MESSAGES['error']} في {step_name}: {str(error)}"
    if use_streamlit:
        import streamlit as st
        st.error(error_msg)
        st.code(traceback.format_exc())
    return False, error_msg


def run_step(step_id: str, use_streamlit: bool = True) -> tuple:
    """تشغيل خطوة معينة وعرض النتائج."""
    step = _find_step_by_id(step_id)
    if not step:
        return False, f"خطوة غير موجودة: {step_id}"
    
    step_name = STEP_NAMES.get(step_id, step["name"])
    try:
        return _execute_step_function(step, step_name, use_streamlit)
    except Exception as e:
        return _handle_run_step_error(step_name, e, use_streamlit)


def _build_step_info(step: dict) -> dict:
    """Build step info dictionary."""
    return {
        "id": step["id"],
        "name": STEP_NAMES.get(step["id"], step["name"]),
        "description": STEP_DESCRIPTIONS.get(step["id"], step["description"]),
        "function": step["function"]
    }


def get_step_info(step_id: str) -> dict:
    """الحصول على معلومات خطوة معينة."""
    for step in AVAILABLE_STEPS:
        if step["id"] == step_id:
            return _build_step_info(step)
    return None


def get_all_steps() -> list:
    """الحصول على جميع الخطوات مع الترجمات."""
    steps = []
    for step in AVAILABLE_STEPS:
        steps.append({
            "id": step["id"],
            "name": STEP_NAMES.get(step["id"], step["name"]),
            "description": STEP_DESCRIPTIONS.get(step["id"], step["description"])
        })
    return steps


def _process_step_with_ui(step: dict, progress_bar, status_text, idx: int, total: int):
    """Process a single step with UI feedback."""
    step_name = STEP_NAMES.get(step['id'], step['name'])
    status_text.text(f"جاري تنفيذ الخطوة {step['id']}: {step_name}")
    
    success, message = run_step(step['id'], use_streamlit=False)
    progress_bar.progress((idx + 1) / total)
    return success, message, step_name


def _cleanup_and_return_failure(progress_bar, status_text, step: dict, step_name: str, message: str) -> tuple:
    """Cleanup UI elements and return failure tuple."""
    import streamlit as st
    progress_bar.empty()
    status_text.empty()
    st.error(f"❌ فشلت الخطوة {step['id']}: {step_name}")
    return False, f"فشلت الخطوة {step['id']}: {message}"


def _cleanup_and_return_success(progress_bar, status_text, step_id: str, target_step_num: int) -> tuple:
    """Cleanup UI elements and return success tuple."""
    progress_bar.empty()
    status_text.empty()
    target_step_name = STEP_NAMES.get(step_id, AVAILABLE_STEPS[target_step_num - 1]['name'])
    return True, f"✅ تم تنفيذ جميع الخطوات حتى الخطوة {step_id}: {target_step_name}"


def _run_with_streamlit_ui(all_steps: list, step_id: str, target_step_num: int) -> tuple:
    """Run steps with Streamlit progress bar."""
    import streamlit as st
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, step in enumerate(all_steps):
        success, message, step_name = _process_step_with_ui(step, progress_bar, status_text, idx, len(all_steps))
        if not success:
            return _cleanup_and_return_failure(progress_bar, status_text, step, step_name, message)
    
    return _cleanup_and_return_success(progress_bar, status_text, step_id, target_step_num)


def _run_without_ui(all_steps: list, step_id: str) -> tuple:
    """Run steps without UI."""
    for step in all_steps:
        success, message = run_step(step['id'], use_streamlit=False)
        if not success:
            return False, f"فشلت الخطوة {step['id']}: {message}"
    return True, f"تم تنفيذ جميع الخطوات حتى الخطوة {step_id} بنجاح"


def run_step_with_dependencies(step_id: str, use_streamlit: bool = True) -> tuple:
    """تشغيل جميع الخطوات من 1 إلى step_id بالترتيب."""
    try:
        target_step_num = int(step_id)
    except ValueError:
        return False, f"معرف خطوة غير صالح: {step_id}"
    
    all_steps = [s for s in AVAILABLE_STEPS if int(s['id']) <= target_step_num]
    
    if not all_steps:
        return False, f"لم يتم العثور على خطوات حتى الخطوة {step_id}"
    
    if use_streamlit:
        return _run_with_streamlit_ui(all_steps, step_id, target_step_num)
    return _run_without_ui(all_steps, step_id)
