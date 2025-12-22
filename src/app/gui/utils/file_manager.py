"""إدارة الملفات والتحميل"""

import os
import zipfile
import streamlit as st
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from src.app.gui.utils.translations import BRANCH_NAMES, CATEGORY_NAMES, MESSAGES


# =============================================================================
# PUBLIC API
# =============================================================================

def list_output_files(directory: str, file_extensions: List[str] = None) -> List[Dict]:
    """قائمة بجميع الملفات في مجلد معين."""
    if file_extensions is None:
        file_extensions = ['.csv', '.xlsx']
    
    if not os.path.exists(directory):
        return []
    
    return sorted(_collect_matching_files(directory, file_extensions), key=lambda file: file["name"])


def read_file_for_display(file_path: str, max_rows: int = 100) -> Optional[pd.DataFrame]:
    """قراءة ملف لعرضه في Streamlit."""
    try:
        if file_path.endswith('.csv'):
            return _read_csv_file_for_display(file_path, max_rows)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path, nrows=max_rows)
    except Exception as error:
        st.error(f"خطأ في قراءة الملف: {str(error)}")
        return None


def create_download_zip(files: List[Dict], zip_name: str = "download.zip") -> bytes:
    """إنشاء ملف ZIP من قائمة الملفات."""
    import io
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_handle:
        _write_files_to_zip(zip_handle, files)
    
    zip_buffer.seek(0)
    return zip_buffer.read()


def get_file_size_str(size_bytes: int) -> str:
    """تحويل حجم الملف إلى نص مقروء."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def organize_files_by_branch(files: List[Dict]) -> Dict[str, List[Dict]]:
    """تنظيم الملفات حسب الفرع."""
    organized = {}
    
    for file_info in files:
        branch = _find_branch_from_path(file_info) or _find_branch_from_filename(file_info) or "other"
        if branch not in organized:
            organized[branch] = []
        organized[branch].append(file_info)
    
    return organized


def organize_files_by_category(files: List[Dict]) -> Dict[str, List[Dict]]:
    """تنظيم الملفات حسب الفئة."""
    organized = {}
    for file_info in files:
        category = _find_category(file_info["name"])
        if category not in organized:
            organized[category] = []
        organized[category].append(file_info)
    return organized


# =============================================================================
# FILE INFO HELPERS
# =============================================================================

def _build_file_info(file_path: str, filename: str, extension: str, directory: str) -> Dict:
    """Build file info dictionary."""
    return {
        "name": filename,
        "path": file_path,
        "relative_path": os.path.relpath(file_path, directory),
        "size": os.path.getsize(file_path),
        "extension": extension
    }


def _collect_matching_files(directory: str, file_extensions: List[str]) -> List[Dict]:
    """Collect files matching extensions."""
    files = []
    for root, directories, filenames in os.walk(directory):
        for filename in filenames:
            _, extension = os.path.splitext(filename)
            if extension.lower() in file_extensions:
                file_path = os.path.join(root, filename)
                files.append(_build_file_info(file_path, filename, extension, directory))
    return files


# =============================================================================
# FILE READING HELPERS
# =============================================================================

def _read_csv_file_for_display(file_path: str, max_rows: int) -> Optional[pd.DataFrame]:
    """Read CSV file with date header detection."""
    with open(file_path, 'r', encoding='utf-8-sig') as file_handle:
        first_line = file_handle.readline().strip()
    
    from src.core.validation.data_validator import extract_dates_from_header
    start_date, end_date = extract_dates_from_header(first_line)
    
    if start_date and end_date:
        return pd.read_csv(file_path, skiprows=1, encoding='utf-8-sig', nrows=max_rows)
    return pd.read_csv(file_path, encoding='utf-8-sig', nrows=max_rows)


# =============================================================================
# ZIP FILE HELPERS
# =============================================================================

def _write_files_to_zip(zip_handle, files: List[Dict]) -> None:
    """Write files to ZIP archive."""
    for file_info in files:
        file_path = file_info.get("path") or file_info.get("file_path")
        file_name = file_info.get("zip_path") or file_info.get("arcname") or file_info.get("name") or file_info.get("file_name")
        if os.path.exists(file_path):
            zip_handle.write(file_path, file_name)


# =============================================================================
# BRANCH FINDING HELPERS
# =============================================================================

def _find_branch_from_path(file_info: Dict) -> str:
    """Find branch name from file path."""
    path_parts = file_info.get("relative_path", "").split(os.sep)
    for part in path_parts:
        if part in BRANCH_NAMES:
            return part
    return None


def _find_branch_from_filename(file_info: Dict) -> str:
    """Find branch name from filename."""
    filename = file_info.get("name", "").lower()
    for key in BRANCH_NAMES.keys():
        if key in filename:
            return key
    return None


# =============================================================================
# CATEGORY FINDING HELPERS
# =============================================================================

def _find_category(filename: str) -> str:
    """Find category for a filename."""
    filename = filename.lower()
    for category_key, category_name in CATEGORY_NAMES.items():
        if f"_{category_key}" in filename or filename.endswith(f"_{category_key}.csv") or filename.endswith(f"_{category_key}.xlsx"):
            return category_key
    return "other"
