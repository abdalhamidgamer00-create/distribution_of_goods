"""Purchases view file management component."""
import os
import streamlit as st
from datetime import datetime
from src.presentation.gui.services.file_service import (
    save_uploaded_file,
    list_files_by_mtime
)

def start_file_management_ui() -> None:
    """Display file upload and selection interface."""
    st.subheader("📁 إدارة الملفات")
    col1, col2 = st.columns(2)
    
    with col1:
        _render_file_uploader()
    
    with col2:
        _render_existing_files()
    
    _render_selection_status()


def _render_file_uploader() -> None:
    """Render file upload section."""
    st.markdown("### 📤 رفع ملف جديد")
    uploaded = st.file_uploader(
        "اختر ملف Excel", 
        type=['xlsx', 'xls'], 
        key="file_uploader"
    )
    if uploaded:
        path = save_uploaded_file(
            uploaded.getbuffer(), 
            uploaded.name, 
            os.path.join("data", "input")
        )
        st.success(f"✅ تم رفع الملف: {uploaded.name}")
        st.session_state['selected_file'] = uploaded.name
        st.session_state['file_source'] = 'uploaded'


def _render_existing_files() -> None:
    """Render validation and selection of existing files."""
    st.markdown("### 📂 استخدام أحدث ملف")
    input_dir = os.path.join("data", "input")
    files = list_files_by_mtime(input_dir, ['.xlsx', '.xls'])
    
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
        type="primary",
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
