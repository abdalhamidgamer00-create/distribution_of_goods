"""صفحة الفائض المتبقي"""

import streamlit as st
import os
import sys
import pandas as pd

# Fix import path for Streamlit Cloud
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.app.gui.utils.file_manager import (
    list_output_files,
    read_file_for_display,
    create_download_zip,
    get_file_size_str,
    organize_files_by_branch,
    organize_files_by_category
)
from src.app.gui.utils.translations import BRANCH_NAMES, CATEGORY_NAMES, MESSAGES

st.set_page_config(
    page_title="الفائض المتبقي",
    page_icon="📦",
    layout="wide"
)

# التحقق من تسجيل الدخول
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()

st.title("📦 الفائض المتبقي")
st.markdown("---")

# مجلدات المخرجات
surplus_csv_dir = os.path.join("data", "output", "remaining_surplus", "csv")
surplus_excel_dir = os.path.join("data", "output", "remaining_surplus", "excel")

# تبويبات للـ CSV و Excel
# تبويبات للـ CSV و Excel
tab1, tab2 = st.tabs(["� ملفات Excel", "� ملفات CSV"])

for tab, directory, file_ext in [(tab1, surplus_excel_dir, ".xlsx"), (tab2, surplus_csv_dir, ".csv")]:
    with tab:
        if not os.path.exists(directory):
            st.warning(f"المجلد غير موجود: {directory}")
            st.info("يرجى تشغيل الخطوة 10 أولاً لإنشاء ملفات الفائض المتبقي")
        else:
            # عرض الملفات
            files = list_output_files(directory, [file_ext])
            
            if not files:
                st.info(MESSAGES["no_files"])
            else:
                st.success(f"تم العثور على {len(files)} ملف")
                
                # تنظيم الملفات حسب الفرع والفئة
                by_branch = organize_files_by_branch(files)
                by_category = organize_files_by_category(files)
                
                # فلتر حسب الفرع
                branch_options = ["الكل"] + [BRANCH_NAMES.get(b, b) for b in sorted(by_branch.keys())]
                selected_branch = st.selectbox("اختر الفرع:", branch_options, key=f"branch_{file_ext}")
                
                # فلتر حسب الفئة
                category_options = ["الكل"] + [CATEGORY_NAMES.get(c, c) for c in sorted(by_category.keys())]
                selected_category = st.selectbox("اختر الفئة:", category_options, key=f"category_{file_ext}")
                
                # تصفية الملفات
                display_files = files
                
                if selected_branch != "الكل":
                    branch_key = None
                    for key, name in BRANCH_NAMES.items():
                        if name == selected_branch:
                            branch_key = key
                            break
                    display_files = [f for f in display_files if branch_key in f['relative_path']]
                
                if selected_category != "الكل":
                    category_key = None
                    for key, name in CATEGORY_NAMES.items():
                        if name == selected_category:
                            category_key = key
                            break
                    display_files = [f for f in display_files if category_key in f['name'].lower()]
                
                # زر تحميل الكل
                if display_files:
                    # Prepare files for zip with organized structure
                    zip_files = []
                    for file_info in display_files:
                        new_info = file_info.copy()
                        # Use relative_path as zip_path to preserve folder structure (e.g. admin/file.xlsx)
                        new_info['zip_path'] = file_info['relative_path']
                        zip_files.append(new_info)
                        
                    zip_data = create_download_zip(zip_files, f"remaining_surplus_{file_ext[1:]}.zip")
                    st.download_button(
                        label=f"📦 تحميل جميع ملفات {file_ext[1:].upper()}",
                        data=zip_data,
                        file_name=f"remaining_surplus_{file_ext[1:]}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                    st.markdown("---")
                
                # عرض كل ملف
                for file_info in display_files:
                    with st.expander(f"📄 {file_info['name']} ({get_file_size_str(file_info['size'])})"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            # قراءة وعرض البيانات
                            df = read_file_for_display(file_info['path'], max_rows=50)
                            if df is not None:
                                st.dataframe(df, use_container_width=True)
                                st.caption(f"عرض أول 50 صف")
                        
                        with col2:
                            # زر التحميل
                            with open(file_info['path'], 'rb') as f:
                                file_data = f.read()
                            
                            st.download_button(
                                label="⬇️ تحميل",
                                data=file_data,
                                file_name=file_info['name'],
                                mime="application/octet-stream",
                                key=f"download_{file_info['name']}_{file_ext}"
                            )

