"""تشغيل خطوات المعالجة من واجهة Streamlit"""

from src.app.pipeline.steps import AVAILABLE_STEPS
from src.app.gui.utils.translations import STEP_NAMES, STEP_DESCRIPTIONS, MESSAGES
import traceback


def run_step(step_id: str, use_streamlit: bool = True) -> tuple:
    """
    تشغيل خطوة معينة وعرض النتائج.
    
    Args:
        step_id: معرف الخطوة (1-11)
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # البحث عن الخطوة
    step = None
    for s in AVAILABLE_STEPS:
        if s["id"] == step_id:
            step = s
            break
    
    if not step:
        return False, f"خطوة غير موجودة: {step_id}"
    
    step_name = STEP_NAMES.get(step_id, step["name"])
    
    try:
        # تشغيل الخطوة
        if use_streamlit:
            import streamlit as st
            with st.spinner(f"{MESSAGES['running']} {step_name}..."):
                result = step["function"](use_latest_file=True)
        else:
            result = step["function"](use_latest_file=True)
        
        if result:
            return True, f"{MESSAGES['success']}: {step_name}"
        else:
            return False, f"{MESSAGES['failed']}: {step_name}"
            
    except Exception as e:
        error_msg = f"{MESSAGES['error']} في {step_name}: {str(e)}"
        if use_streamlit:
            import streamlit as st
            st.error(error_msg)
            st.code(traceback.format_exc())
        return False, error_msg


def get_step_info(step_id: str) -> dict:
    """
    الحصول على معلومات خطوة معينة.
    
    Args:
        step_id: معرف الخطوة
        
    Returns:
        Dictionary with step information
    """
    for step in AVAILABLE_STEPS:
        if step["id"] == step_id:
            return {
                "id": step["id"],
                "name": STEP_NAMES.get(step["id"], step["name"]),
                "description": STEP_DESCRIPTIONS.get(step["id"], step["description"]),
                "function": step["function"]
            }
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


def run_step_with_dependencies(step_id: str, use_streamlit: bool = True) -> tuple:
    """
    تشغيل جميع الخطوات من 1 إلى step_id بالترتيب.
    
    Args:
        step_id: معرف الخطوة المستهدفة
        use_streamlit: استخدام مكونات Streamlit للواجهة
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # الحصول على جميع الخطوات حتى الخطوة المستهدفة
    try:
        target_step_num = int(step_id)
    except ValueError:
        return False, f"معرف خطوة غير صالح: {step_id}"
    
    all_steps = [s for s in AVAILABLE_STEPS if int(s['id']) <= target_step_num]
    
    if not all_steps:
        return False, f"لم يتم العثور على خطوات حتى الخطوة {step_id}"
    
    if use_streamlit:
        import streamlit as st
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, step in enumerate(all_steps):
            step_name = STEP_NAMES.get(step['id'], step['name'])
            status_text.text(f"جاري تنفيذ الخطوة {step['id']}: {step_name}")
            
            # تشغيل الخطوة بدون واجهة Streamlit لتجنب التداخل
            success, message = run_step(step['id'], use_streamlit=False)
            
            if not success:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ فشلت الخطوة {step['id']}: {step_name}")
                st.error(message)
                return False, f"فشلت الخطوة {step['id']}: {message}"
            
            progress_bar.progress((idx + 1) / len(all_steps))
        
        progress_bar.empty()
        status_text.empty()
        target_step_name = STEP_NAMES.get(step_id, AVAILABLE_STEPS[target_step_num - 1]['name'])
        return True, f"✅ تم تنفيذ جميع الخطوات حتى الخطوة {step_id}: {target_step_name}"
    else:
        # تشغيل بدون واجهة
        for step in all_steps:
            success, message = run_step(step['id'], use_streamlit=False)
            if not success:
                return False, f"فشلت الخطوة {step['id']}: {message}"
        
        return True, f"تم تنفيذ جميع الخطوات حتى الخطوة {step_id} بنجاح"
