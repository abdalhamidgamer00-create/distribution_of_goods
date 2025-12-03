"""صفحة النقص"""

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
    organize_files_by_category
)
from src.app.gui.utils.translations import CATEGORY_NAMES, MESSAGES

st.set_page_config(
    page_title="النقص",
    page_icon="⚠️",
    layout="wide"
)

# التحقق من تسجيل الدخول
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()

st.title("⚠️ النقص في المنتجات")
st.markdown("---")

# مجلدات المخرجات
shortage_csv_dir = os.path.join("data", "output", "shortage", "csv")
shortage_excel_dir = os.path.join("data", "output", "shortage", "excel")

# تبويبات للـ CSV و Excel
tab1, tab2 = st.tabs(["� ملفات Excel", "� ملفات CSV"])

for tab, directory, file_ext in [(tab1, shortage_excel_dir, ".xlsx"), (tab2, shortage_csv_dir, ".csv")]:
    with tab:
        if not os.path.exists(directory):
            st.warning(f"المجلد غير موجود: {directory}")
            st.info("يرجى تشغيل الخطوة 11 أولاً لإنشاء ملفات النقص")
        else:
            # عرض الملفات
            files = list_output_files(directory, [file_ext])
            
            if not files:
                st.info(MESSAGES["no_files"])
            else:
                st.success(f"تم العثور على {len(files)} ملف")
                
                # تنظيم الملفات حسب الفئة
                by_category = organize_files_by_category(files)
                
                # فلتر حسب الفئة
                category_options = ["الكل"] + [CATEGORY_NAMES.get(c, c) for c in sorted(by_category.keys())]
                selected_category = st.selectbox("اختر الفئة:", category_options, key=f"category_{file_ext}")
                
                # تصفية الملفات
                display_files = files
                
                if selected_category != "الكل":
                    category_key = None
                    for key, name in CATEGORY_NAMES.items():
                        if name == selected_category:
                            category_key = key
                            break
                    display_files = [f for f in display_files if category_key in f['name'].lower() or f['name'].endswith(f"_{category_key}{file_ext}")]
                
                # زر تحميل الكل
                if display_files:
                    zip_data = create_download_zip(display_files, f"shortage_{file_ext[1:]}.zip")
                    st.download_button(
                        label=f"📦 تحميل جميع ملفات {file_ext[1:].upper()}",
                        data=zip_data,
                        file_name=f"shortage_{file_ext[1:]}.zip",
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
                            df = read_file_for_display(file_info['path'], max_rows=100)
                            if df is not None:
                                st.dataframe(df, use_container_width=True)
                                
                                # إحصائيات سريعة
                                if 'shortage_quantity' in df.columns:
                                    total_shortage = df['shortage_quantity'].sum()
                                    st.metric("إجمالي النقص", f"{int(total_shortage):,} وحدة")
                                
                                st.caption(f"عرض أول 100 صف")
                        
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

