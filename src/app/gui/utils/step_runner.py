"""تشغيل خطوات المعالجة من واجهة Streamlit"""
import traceback
from typing import Tuple, Optional, Dict, List, Any
from src.app.pipeline.steps import AVAILABLE_STEPS
from src.app.gui.utils.translations import (
    STEP_NAMES, 
    STEP_DESCRIPTIONS, 
    MESSAGES
)


# =============================================================================
# PUBLIC API
# =============================================================================

def run_step(step_id: str, use_streamlit: bool = True) -> Tuple[bool, str]:
    """تشغيل خطوة معينة وعرض النتائج."""
    step = _find_step_by_id(step_id)
    if not step:
        return False, f"خطوة غير موجودة: {step_id}"
    
    step_name = STEP_NAMES.get(step_id, step["name"])
    
    try:
        return _execute_step_function(step, step_name, use_streamlit)
    except Exception as error:
        return _handle_run_step_error(step_name, error, use_streamlit)


def get_step_info(step_id: str) -> Optional[Dict]:
    """الحصول على معلومات خطوة معينة."""
    for step in AVAILABLE_STEPS:
        if step["id"] == step_id:
            return _build_step_info(step)
    return None


def get_all_steps() -> List[Dict]:
    """الحصول على جميع الخطوات مع الترجمات."""
    steps = []
    
    for step in AVAILABLE_STEPS:
        steps.append({
            "id": step["id"],
            "name": STEP_NAMES.get(step["id"], step["name"]),
            "description": STEP_DESCRIPTIONS.get(
                step["id"], 
                step["description"]
            )
        })
        
    return steps


def run_step_with_dependencies(
    step_id: str, 
    use_streamlit: bool = True
) -> Tuple[bool, str]:
    """تشغيل جميع الخطوات من 1 إلى step_id بالترتيب."""
    valid, result = _validate_step_id(step_id)
    
    if not valid:
        return False, str(result)
        
    target_step_number = int(result)
    
    all_steps = [
        step for step in AVAILABLE_STEPS 
        if int(step['id']) <= target_step_number
    ]
    
    if not all_steps:
        return False, f"لم يتم العثور على خطوات حتى الخطوة {step_id}"
        
    if use_streamlit:
        return _run_with_streamlit_ui(
            all_steps, 
            step_id, 
            target_step_number
        )
        
    return _run_without_ui(all_steps, step_id)


# =============================================================================
# PRIVATE HELPERS: LOOKUP & VALIDATION
# =============================================================================

def _find_step_by_id(step_id: str) -> Optional[Dict]:
    """Find step by its ID."""
    for step in AVAILABLE_STEPS:
        if step["id"] == step_id:
            return step
    return None


def _build_step_info(step: dict) -> Dict:
    """Build step info dictionary."""
    return {
        "id": step["id"],
        "name": STEP_NAMES.get(step["id"], step["name"]),
        "description": STEP_DESCRIPTIONS.get(
            step["id"], 
            step["description"]
        ),
        "function": step["function"]
    }


def _validate_step_id(step_id: str) -> Tuple[bool, Any]:
    """Validate step_id and return (success, target_step_num/error)."""
    try:
        return True, int(step_id)
    except ValueError:
        return False, f"معرف خطوة غير صالح: {step_id}"


# =============================================================================
# PRIVATE HELPERS: EXECUTION LOGIC
# =============================================================================

def _execute_step_function(
    step: Dict, 
    step_name: str, 
    use_streamlit: bool
) -> Tuple[bool, str]:
    """Execute step function with optional Streamlit spinner."""
    result = False
    
    if use_streamlit:
        import streamlit as st
        with st.spinner(f"{MESSAGES['running']} {step_name}..."):
            result = step["function"](use_latest_file=True)
    else:
        result = step["function"](use_latest_file=True)
        
    if result:
        return True, f"{MESSAGES['success']}: {step_name}"
    
    return False, f"{MESSAGES['failed']}: {step_name}"


def _handle_run_step_error(
    step_name: str, 
    error: Exception, 
    use_streamlit: bool
) -> Tuple[bool, str]:
    """Handle step execution error."""
    error_message = f"{MESSAGES['error']} في {step_name}: {str(error)}"
    
    if use_streamlit:
        import streamlit as st
        st.error(error_message)
        st.code(traceback.format_exc())
        
    return False, error_message


# =============================================================================
# PRIVATE HELPERS: UI ORCHESTRATION
# =============================================================================

def _run_with_streamlit_ui(
    all_steps: List[Dict], 
    step_id: str, 
    target_step_number: int
) -> Tuple[bool, str]:
    """Run steps with Streamlit progress bar."""
    import streamlit as st
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, step in enumerate(all_steps):
        success, msg, name = _process_step_with_ui(
            step, 
            progress_bar, 
            status_text, 
            idx, 
            len(all_steps)
        )
        
        if not success:
            return _cleanup_failure(
                progress_bar, 
                status_text, 
                step['id'], 
                name, 
                msg
            )
            
    return _cleanup_success(
        progress_bar, 
        status_text, 
        step_id, 
        target_step_number
    )


def _run_without_ui(
    all_steps: List[Dict], 
    step_id: str
) -> Tuple[bool, str]:
    """Run steps without UI."""
    for step in all_steps:
        success, message = run_step(
            step['id'], 
            use_streamlit=False
        )
        
        if not success:
            return False, f"فشلت الخطوة {step['id']}: {message}"
            
    return True, f"تم تنفيذ جميع الخطوات حتى الخطوة {step_id} بنجاح"


def _process_step_with_ui(
    step: Dict, 
    progress_bar: Any, 
    status_text: Any, 
    step_index: int, 
    total: int
) -> Tuple[bool, str, str]:
    """Process a single step with UI feedback."""
    step_name = STEP_NAMES.get(step['id'], step['name'])
    status_text.text(f"جاري تنفيذ الخطوة {step['id']}: {step_name}")
    
    success, message = run_step(step['id'], use_streamlit=False)
    
    progress_bar.progress((step_index + 1) / total)
    return success, message, step_name


def _cleanup_failure(
    progress_bar: Any, 
    status_text: Any, 
    step_id: str, 
    step_name: str, 
    message: str
) -> Tuple[bool, str]:
    """Cleanup UI elements and return failure tuple."""
    import streamlit as st
    
    progress_bar.empty()
    status_text.empty()
    
    st.error(f"❌ فشلت الخطوة {step_id}: {step_name}")
    return False, f"فشلت الخطوة {step_id}: {message}"


def _cleanup_success(
    progress_bar: Any, 
    status_text: Any, 
    step_id: str, 
    target_step_number: int
) -> Tuple[bool, str]:
    """Cleanup UI elements and return success tuple."""
    progress_bar.empty()
    status_text.empty()
    
    target = AVAILABLE_STEPS[target_step_number - 1]
    name = STEP_NAMES.get(step_id, target['name'])
    
    return True, f"✅ تم تنفيذ جميع الخطوات حتى الخطوة {step_id}: {name}"
