"""قسم المشتريات - نظام توزيع البضائع"""

import streamlit as st
import sys
import os
from datetime import datetime

# Fix import path for Streamlit Cloud
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app.gui.utils.step_runner import run_step, get_all_steps, run_step_with_dependencies
from src.app.gui.utils.translations import MESSAGES

st.set_page_config(
    page_title="قسم المشتريات",
    page_icon="🛒",
    layout="wide"
)

# التحقق من تسجيل الدخول
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()


def show_metrics():
    """Display quick metrics about files and branches"""
    col1, col2 = st.columns(2)
    
    output_dir = os.path.join("data", "output")
    if os.path.exists(output_dir):
        file_count = sum([len(files) for r, d, files in os.walk(output_dir)])
        col1.metric("عدد الملفات", file_count)
    else:
        col1.metric("عدد الملفات", 0)
    
    col2.metric("عدد الفروع", 6)


def _save_uploaded_file(uploaded_file) -> None:
    """Save uploaded file to input directory."""
    input_dir = os.path.join("data", "input")
    os.makedirs(input_dir, exist_ok=True)
    save_path = os.path.join(input_dir, uploaded_file.name)
    
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"✅ تم رفع الملف: {uploaded_file.name}")
    st.session_state['selected_file'] = uploaded_file.name
    st.session_state['file_source'] = 'uploaded'


def _show_upload_section() -> None:
    """Display file upload section."""
    st.markdown("### � رفع ملف جديد")
    uploaded_file = st.file_uploader(
        "اختر ملف Excel",
        type=['xlsx', 'xls'],
        help="قم برفع ملف Excel من جهازك",
        key="file_uploader"
    )
    if uploaded_file is not None:
        _save_uploaded_file(uploaded_file)


def _display_latest_file_info(input_dir: str, latest_file: str) -> None:
    """Display latest file information and selection button."""
    file_path = os.path.join(input_dir, latest_file)
    file_size = os.path.getsize(file_path) / 1024
    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
    
    st.info(f"📄 **{latest_file}**")
    st.caption(f"الحجم: {file_size:.2f} KB")
    st.caption(f"آخر تعديل: {file_mtime.strftime('%Y-%m-%d %H:%M')}")
    
    if st.button("استخدام هذا الملف", key="use_latest", use_container_width=True):
        st.session_state['selected_file'] = latest_file
        st.session_state['file_source'] = 'existing'
        st.success(f"✅ تم اختيار: {latest_file}")


def _get_sorted_excel_files(input_dir: str) -> list:
    """Get Excel files sorted by modification time."""
    if not os.path.exists(input_dir):
        return None
    excel_files = [f for f in os.listdir(input_dir) if f.endswith(('.xlsx', '.xls'))]
    excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(input_dir, x)), reverse=True)
    return excel_files


def _show_latest_file_section() -> None:
    """Display latest file selection section."""
    st.markdown("### 📂 استخدام أحدث ملف")
    input_dir = os.path.join("data", "input")
    
    excel_files = _get_sorted_excel_files(input_dir)
    if excel_files is None:
        st.error("❌ مجلد البيانات غير موجود")
    elif excel_files:
        _display_latest_file_info(input_dir, excel_files[0])
    else:
        st.warning("⚠️ لا توجد ملفات Excel في المجلد")


def _show_selected_file_status() -> None:
    """Display currently selected file status."""
    if 'selected_file' in st.session_state:
        source_text = "مرفوع" if st.session_state.get('file_source') == 'uploaded' else "موجود"
        st.success(f"✅ الملف المختار حالياً: **{st.session_state['selected_file']}** ({source_text})")
    else:
        st.warning("⚠️ لم يتم اختيار ملف بعد. يرجى رفع ملف أو اختيار أحدث ملف.")


def show_file_management():
    """Display file upload and selection interface"""
    st.subheader("📁 إدارة الملفات")
    
    col1, col2 = st.columns(2)
    with col1:
        _show_upload_section()
    with col2:
        _show_latest_file_section()
    
    _show_selected_file_status()


NAV_BUTTON_CONFIG = {
    '8': [("📤 عرض ملفات التحويل", "pages/06_ملفات_التحويل.py")],
    '9': [("📦 عرض الفائض المتبقي", "pages/07_الفائض_المتبقي.py")],
    '10': [("⚠️ عرض ملفات النقص", "pages/08_النقص.py")],
    '11': [("📋 التحويلات المجمعة", "pages/09_التحويلات_المجمعة.py"),
           ("📂 التحويلات المنفصلة", "pages/10_التحويلات_المنفصلة.py")]
}


def _render_nav_buttons(step_id: str, buttons: list) -> None:
    """Render navigation buttons for a step."""
    cols = st.columns(len(buttons))
    for idx, (label, page) in enumerate(buttons):
        with cols[idx]:
            if st.button(label, key=f"nav_{step_id}_{idx}", type="primary", use_container_width=True):
                st.switch_page(page)


def show_navigation_button(step_id):
    """Display navigation button for specific step if successful"""
    if step_id in NAV_BUTTON_CONFIG and st.session_state.get(f'step_{step_id}_success', False):
        _render_nav_buttons(step_id, NAV_BUTTON_CONFIG[step_id])


def _run_step_and_display(step: dict) -> None:
    """Run a step with dependencies and display result."""
    if 'selected_file' not in st.session_state:
        st.error("❌ يرجى اختيار ملف أولاً من قسم إدارة الملفات أعلاه")
        return
    
    success, message = run_step_with_dependencies(step['id'])
    st.session_state[f'step_{step["id"]}_success'] = success
    st.success(message) if success else st.error(message)


def _display_step_card(step: dict) -> None:
    """Display a single step card with run button."""
    with st.container():
        st.markdown(f"### {step['name']}")
        st.caption(step['description'])
        
        if st.button(f"▶️ تشغيل مع الخطوات السابقة", key=f"run_{step['id']}"):
            _run_step_and_display(step)
        
        show_navigation_button(step['id'])
        st.markdown("---")


def show_steps():
    """Display available steps with run buttons"""
    st.subheader("الخطوات المتاحة")
    
    steps = get_all_steps()
    visible_steps = [step for step in steps if step['id'] in ['8', '9', '10', '11']]
    
    cols = st.columns(len(visible_steps))
    for idx, step in enumerate(visible_steps):
        with cols[idx]:
            _display_step_card(step)


def _execute_steps_with_progress(steps: list, progress_bar, status_text) -> bool:
    """Execute all steps with progress tracking."""
    for idx, step in enumerate(steps):
        status_text.text(f"جاري تنفيذ: {step['name']}")
        success, message = run_step(step['id'])
        
        if not success:
            st.error(f"فشل في: {step['name']}")
            return False
        
        progress_bar.progress((idx + 1) / len(steps))
    return True


def _run_all_steps_ui() -> None:
    """Run all steps with progress UI."""
    steps = get_all_steps()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    if _execute_steps_with_progress(steps, progress_bar, status_text):
        status_text.text("اكتمل تنفيذ جميع الخطوات!")
        st.success("✅ تم تنفيذ جميع الخطوات بنجاح!")
        st.session_state['all_steps_success'] = True


def show_run_all_steps():
    """Display run all steps button and progress"""
    st.markdown("---")
    st.subheader("تشغيل جميع الخطوات")
    
    if st.button("🚀 تشغيل جميع الخطوات بالترتيب", type="primary", use_container_width=True):
        if 'selected_file' not in st.session_state:
            st.error("❌ يرجى اختيار ملف أولاً من قسم إدارة الملفات أعلاه")
        else:
            _run_all_steps_ui()


NAV_BUTTONS = [
    ("📤 ملفات التحويل", "nav_all_transfer", "pages/06_ملفات_التحويل.py"),
    ("📦 الفائض المتبقي", "nav_all_surplus", "pages/07_الفائض_المتبقي.py"),
    ("⚠️ ملفات النقص", "nav_all_shortage", "pages/08_النقص.py"),
    ("📋 مجمعة", "nav_all_combined", "pages/09_التحويلات_المجمعة.py"),
    ("📂 منفصلة", "nav_all_separate", "pages/10_التحويلات_المنفصلة.py"),
]


def show_results_navigation():
    """Display navigation buttons to result pages if all steps succeeded"""
    if not st.session_state.get('all_steps_success', False):
        return
    
    st.markdown("### 📂 عرض النتائج")
    cols = st.columns(len(NAV_BUTTONS))
    for col, (label, key, page) in zip(cols, NAV_BUTTONS):
        with col:
            if st.button(label, key=key, use_container_width=True):
                st.switch_page(page)


# Main page layout
st.title("🛒 قسم المشتريات")
st.markdown("### نظام توزيع البضائع")
st.markdown("---")

show_metrics()
st.markdown("---")

show_file_management()
st.markdown("---")

show_steps()

show_run_all_steps()
show_results_navigation()

# Back button
st.markdown("---")
if st.button("← العودة إلى الرئيسية"):
    st.switch_page("pages/00_الرئيسية.py")
