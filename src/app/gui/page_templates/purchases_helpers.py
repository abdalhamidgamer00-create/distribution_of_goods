"""Helper functions for purchases page."""

import streamlit as st
import os
from datetime import datetime

from src.app.gui.utils.step_runner import run_step, get_all_steps, run_step_with_dependencies


# =============================================================================
# CONSTANTS
# =============================================================================

NAV_BUTTON_CONFIG = {
    '8': [("📤 عرض ملفات التحويل", "pages/06_ملفات_التحويل.py")],
    '9': [("📦 عرض الفائض المتبقي", "pages/07_الفائض_المتبقي.py")],
    '10': [("⚠️ عرض ملفات النقص", "pages/08_النقص.py")],
    '11': [("📋 التحويلات المجمعة", "pages/09_التحويلات_المجمعة.py"),
           ("📂 التحويلات المنفصلة", "pages/10_التحويلات_المنفصلة.py")]
}

NAV_BUTTONS = [
    ("📤 ملفات التحويل", "nav_all_transfer", "pages/06_ملفات_التحويل.py"),
    ("📦 الفائض المتبقي", "nav_all_surplus", "pages/07_الفائض_المتبقي.py"),
    ("⚠️ ملفات النقص", "nav_all_shortage", "pages/08_النقص.py"),
    ("📋 مجمعة", "nav_all_combined", "pages/09_التحويلات_المجمعة.py"),
    ("📂 منفصلة", "nav_all_separate", "pages/10_التحويلات_المنفصلة.py"),
]


# =============================================================================
# METRICS
# =============================================================================

def show_metrics():
    """Display quick metrics about files and branches."""
    col1, col2 = st.columns(2)
    output_dir = os.path.join("data", "output")
    file_count = sum(len(f) for _, _, f in os.walk(output_dir)) if os.path.exists(output_dir) else 0
    col1.metric("عدد الملفات", file_count)
    col2.metric("عدد الفروع", 6)


# =============================================================================
# FILE MANAGEMENT
# =============================================================================

def save_uploaded_file(uploaded_file) -> None:
    """Save uploaded file to input directory."""
    input_dir = os.path.join("data", "input")
    os.makedirs(input_dir, exist_ok=True)
    with open(os.path.join(input_dir, uploaded_file.name), "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ تم رفع الملف: {uploaded_file.name}")
    st.session_state['selected_file'] = uploaded_file.name
    st.session_state['file_source'] = 'uploaded'


def get_excel_files(input_dir: str) -> list:
    """Get Excel files sorted by modification time."""
    if not os.path.exists(input_dir):
        return None
    files = [f for f in os.listdir(input_dir) if f.endswith(('.xlsx', '.xls'))]
    return sorted(files, key=lambda x: os.path.getmtime(os.path.join(input_dir, x)), reverse=True)


def show_file_management():
    """Display file upload and selection interface."""
    st.subheader("📁 إدارة الملفات")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 رفع ملف جديد")
        uploaded = st.file_uploader("اختر ملف Excel", type=['xlsx', 'xls'], key="file_uploader")
        if uploaded:
            save_uploaded_file(uploaded)
    
    with col2:
        st.markdown("### 📂 استخدام أحدث ملف")
        input_dir = os.path.join("data", "input")
        files = get_excel_files(input_dir)
        if files is None:
            st.error("❌ مجلد البيانات غير موجود")
        elif files:
            latest = files[0]
            path = os.path.join(input_dir, latest)
            st.info(f"📄 **{latest}**")
            st.caption(f"الحجم: {os.path.getsize(path)/1024:.2f} KB | آخر تعديل: {datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M')}")
            if st.button("استخدام هذا الملف", key="use_latest", use_container_width=True):
                st.session_state['selected_file'] = latest
                st.session_state['file_source'] = 'existing'
                st.success(f"✅ تم اختيار: {latest}")
        else:
            st.warning("⚠️ لا توجد ملفات Excel")
    
    # Status
    if 'selected_file' in st.session_state:
        src = "مرفوع" if st.session_state.get('file_source') == 'uploaded' else "موجود"
        st.success(f"✅ الملف المختار: **{st.session_state['selected_file']}** ({src})")
    else:
        st.warning("⚠️ لم يتم اختيار ملف بعد")


# =============================================================================
# STEP EXECUTION
# =============================================================================

def run_step_with_display(step: dict) -> None:
    """Run a step with dependencies and display result."""
    if 'selected_file' not in st.session_state:
        st.error("❌ يرجى اختيار ملف أولاً")
        return
    success, message = run_step_with_dependencies(step['id'])
    st.session_state[f'step_{step["id"]}_success'] = success
    st.success(message) if success else st.error(message)


def run_all_steps():
    """Run all steps with progress UI."""
    if 'selected_file' not in st.session_state:
        st.error("❌ يرجى اختيار ملف أولاً")
        return
    
    steps = get_all_steps()
    progress = st.progress(0)
    status = st.empty()
    
    for i, step in enumerate(steps):
        status.text(f"جاري تنفيذ: {step['name']}")
        success, _ = run_step(step['id'])
        if not success:
            st.error(f"فشل في: {step['name']}")
            return
        progress.progress((i + 1) / len(steps))
    
    status.text("اكتمل تنفيذ جميع الخطوات!")
    st.success("✅ تم تنفيذ جميع الخطوات بنجاح!")
    st.session_state['all_steps_success'] = True


# =============================================================================
# NAVIGATION
# =============================================================================

def show_nav_button(step_id: str):
    """Display navigation button for specific step if successful."""
    if step_id in NAV_BUTTON_CONFIG and st.session_state.get(f'step_{step_id}_success', False):
        buttons = NAV_BUTTON_CONFIG[step_id]
        cols = st.columns(len(buttons))
        for i, (label, page) in enumerate(buttons):
            with cols[i]:
                if st.button(label, key=f"nav_{step_id}_{i}", type="primary", use_container_width=True):
                    st.switch_page(page)


def show_results_navigation():
    """Display navigation buttons to result pages if all steps succeeded."""
    if not st.session_state.get('all_steps_success', False):
        return
    st.markdown("### 📂 عرض النتائج")
    cols = st.columns(len(NAV_BUTTONS))
    for col, (label, key, page) in zip(cols, NAV_BUTTONS):
        with col:
            if st.button(label, key=key, use_container_width=True):
                st.switch_page(page)
