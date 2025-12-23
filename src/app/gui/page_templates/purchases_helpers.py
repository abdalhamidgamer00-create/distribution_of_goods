"""Helper functions for purchases page."""
import streamlit as st
import os
from datetime import datetime
from src.app.gui.utils.step_runner import (
    run_step,
    get_all_steps, 
    run_step_with_dependencies
)


# =============================================================================
# CONSTANTS
# =============================================================================

NAV_BUTTON_CONFIG = {
    '8': [("📤 عرض ملفات التحويل", "pages/06_ملفات_التحويل.py")],
    '9': [("📦 عرض الفائض المتبقي", "pages/07_الفائض_المتبقي.py")],
    '10': [("⚠️ عرض ملفات النقص", "pages/08_النقص.py")],
    '11': [
        ("📋 التحويلات المجمعة", "pages/09_التحويلات_المجمعة.py"),
        ("📂 التحويلات المنفصلة", "pages/10_التحويلات_المنفصلة.py")
    ]
}

NAV_BUTTONS = [
    ("📤 ملفات التحويل", "nav_all_transfer", "pages/06_ملفات_التحويل.py"),
    ("📦 الفائض المتبقي", "nav_all_surplus", "pages/07_الفائض_المتبقي.py"),
    ("⚠️ ملفات النقص", "nav_all_shortage", "pages/08_النقص.py"),
    ("📋 مجمعة", "nav_all_combined", "pages/09_التحويلات_المجمعة.py"),
    ("📂 منفصلة", "nav_all_separate", "pages/10_التحويلات_المنفصلة.py"),
]


# =============================================================================
# PUBLIC API
# =============================================================================

def show_metrics() -> None:
    """Display quick metrics about files and branches."""
    col1, col2 = st.columns(2)
    output_dir = os.path.join("data", "output")
    
    file_count = 0
    if os.path.exists(output_dir):
        file_count = sum(len(f) for _, _, f in os.walk(output_dir))
        
    col1.metric("عدد الملفات", file_count)
    col2.metric("عدد الفروع", 6)


def start_file_management_ui() -> None:
    """Display file upload and selection interface."""
    st.subheader("📁 إدارة الملفات")
    col1, col2 = st.columns(2)
    
    with col1:
        _render_file_uploader()
    
    with col2:
        _render_existing_files()
    
    _render_selection_status()


def execute_step_ui(step: dict) -> None:
    """Run a step with dependencies and display result."""
    if 'selected_file' not in st.session_state:
        st.error("❌ يرجى اختيار ملف أولاً")
        return

    success, message = run_step_with_dependencies(step['id'])
    st.session_state[f'step_{step["id"]}_success'] = success
    
    if success:
        st.success(message)
    else:
        st.error(message)


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
        success, _ = run_step(step['id'])
        
        if not success:
            st.error(f"فشل في: {step['name']}")
            return
            
        progress.progress((i + 1) / len(steps))
    
    status.text("اكتمل تنفيذ جميع الخطوات!")
    st.success("✅ تم تنفيذ جميع الخطوات بنجاح!")
    st.session_state['all_steps_success'] = True


def render_nav_button(step_id: str) -> None:
    """Display navigation button for specific step if successful."""
    allowed = (
        step_id in NAV_BUTTON_CONFIG and 
        st.session_state.get(f'step_{step_id}_success', False)
    )
    
    if not allowed:
        return
        
    buttons = NAV_BUTTON_CONFIG[step_id]
    cols = st.columns(len(buttons))
    
    for i, (label, page) in enumerate(buttons):
        with cols[i]:
            if st.button(
                label, 
                key=f"nav_{step_id}_{i}", 
                type="primary", 
                use_container_width=True
            ):
                st.switch_page(page)


def render_results_navigation() -> None:
    """Display navigation buttons to result pages if all steps succeeded."""
    if not st.session_state.get('all_steps_success', False):
        return
        
    st.markdown("### 📂 عرض النتائج")
    cols = st.columns(len(NAV_BUTTONS))
    
    for col, (label, key, page) in zip(cols, NAV_BUTTONS):
        with col:
            if st.button(label, key=key, use_container_width=True):
                st.switch_page(page)


def save_uploaded_file(uploaded_file) -> None:
    """Save uploaded file to input directory."""
    input_dir = os.path.join("data", "input")
    os.makedirs(input_dir, exist_ok=True)
    
    file_path = os.path.join(input_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.success(f"✅ تم رفع الملف: {uploaded_file.name}")
    st.session_state['selected_file'] = uploaded_file.name
    st.session_state['file_source'] = 'uploaded'


def fetch_excel_files(input_dir: str) -> list:
    """Get Excel files sorted by modification time."""
    if not os.path.exists(input_dir):
        return None
        
    files = [
        f for f in os.listdir(input_dir) 
        if f.endswith(('.xlsx', '.xls'))
    ]
    
    return sorted(
        files, 
        key=lambda x: os.path.getmtime(os.path.join(input_dir, x)), 
        reverse=True
    )


# =============================================================================
# PRIVATE HELPERS
# =============================================================================

def _render_file_uploader() -> None:
    """Render file upload section."""
    st.markdown("### 📤 رفع ملف جديد")
    uploaded = st.file_uploader(
        "اختر ملف Excel", 
        type=['xlsx', 'xls'], 
        key="file_uploader"
    )
    if uploaded:
        save_uploaded_file(uploaded)


def _render_existing_files() -> None:
    """Render validation and selection of existing files."""
    st.markdown("### 📂 استخدام أحدث ملف")
    input_dir = os.path.join("data", "input")
    files = fetch_excel_files(input_dir)
    
    if files is None:
        st.error("❌ مجلد البيانات غير موجود")
        return
        
    if not files:
        st.warning("⚠️ لا توجد ملفات Excel")
        return
        
    _display_latest_file(input_dir, files[0])


def _display_latest_file(input_dir: str, latest: str) -> None:
    """Display information about the latest file."""
    path = os.path.join(input_dir, latest)
    size_kb = os.path.getsize(path) / 1024
    mtime = datetime.fromtimestamp(os.path.getmtime(path))
    date_str = mtime.strftime('%Y-%m-%d %H:%M')
    
    st.info(f"📄 **{latest}**")
    st.caption(f"الحجم: {size_kb:.2f} KB | آخر تعديل: {date_str}")
    
    if st.button(
        "استخدام هذا الملف", 
        key="use_latest", 
        use_container_width=True
    ):
        st.session_state['selected_file'] = latest
        st.session_state['file_source'] = 'existing'
        st.success(f"✅ تم اختيار: {latest}")


def _render_selection_status() -> None:
    """Render current file selection status."""
    if 'selected_file' in st.session_state:
        src_type = st.session_state.get('file_source')
        src = "مرفوع" if src_type == 'uploaded' else "موجود"
        filename = st.session_state['selected_file']
        st.success(f"✅ الملف المختار: **{filename}** ({src})")
    else:
        st.warning("⚠️ لم يتم اختيار ملف بعد")
