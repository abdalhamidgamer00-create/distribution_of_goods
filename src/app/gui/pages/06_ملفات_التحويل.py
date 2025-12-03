"""صفحة ملفات التحويل"""

import streamlit as st
import os
import pandas as pd
from src.app.gui.utils.file_manager import (
    list_output_files,
    read_file_for_display,
    create_download_zip,
    get_file_size_str,
    organize_files_by_branch
)
from src.app.gui.utils.translations import BRANCH_NAMES, CATEGORY_NAMES, MESSAGES
from src.core.domain.branches.config import get_branches

st.set_page_config(
    page_title="ملفات التحويل",
    page_icon="📤",
    layout="wide"
)

# التحقق من تسجيل الدخول
from src.app.gui.utils.auth import check_password
if not check_password():
    st.stop()

st.title("📤 ملفات التحويل")
st.markdown("---")

# Branch selection buttons
st.subheader("📍 اختر الفرع المصدر")
st.caption("اختر فرع لعرض جميع التحويلات منه إلى الفروع الأخرى")

branches = get_branches()
branch_labels = {
    'admin': '🏢 الإدارة',
    'asherin': '🏪 العشرين',
    'wardani': '🏬 الورداني',
    'akba': '🏭 العقبي',
    'shahid': '🏗️ الشهيد',
    'nujum': '⭐ النجوم'
}

# Create 7 buttons (All + 6 branches)
# First row: All (full width or centered)
if st.button("🌐 كل الفروع", key="branch_btn_all", use_container_width=True):
    st.session_state['selected_source_branch'] = 'all'

# Remaining 6 buttons in 3 columns
col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3, col1, col2, col3]

for idx, branch in enumerate(branches):
    with cols[idx]:
        if st.button(branch_labels.get(branch, branch), key=f"branch_btn_{branch}", use_container_width=True):
            st.session_state['selected_source_branch'] = branch

# Show selected branch
if 'selected_source_branch' in st.session_state:
    selected = st.session_state['selected_source_branch']
    if selected == 'all':
        st.info(f"📂 عرض التحويلات من: **كل الفروع** → الفروع الأخرى")
    else:
        st.info(f"📂 عرض التحويلات من: **{branch_labels.get(selected, selected)}** → الفروع الأخرى")
else:
    st.warning("⚠️ يرجى اختيار فرع من الأزرار أعلاه")

st.markdown("---")

# مجلدات المخرجات
transfers_csv_dir = os.path.join("data", "output", "transfers", "csv")
transfers_excel_dir = os.path.join("data", "output", "transfers", "excel")

# Only show files if a branch is selected
if 'selected_source_branch' in st.session_state:
    selected_branch = st.session_state['selected_source_branch']
    
    # تبويبات للـ CSV و Excel
    tab1, tab2 = st.tabs(["📊 ملفات Excel", "📄 ملفات CSV"])
    
    for tab, directory, file_ext in [(tab1, transfers_excel_dir, ".xlsx"), (tab2, transfers_csv_dir, ".csv")]:
        with tab:
            if not os.path.exists(directory):
                st.warning(f"المجلد غير موجود: {directory}")
                st.info("يرجى تشغيل الخطوة 7 أولاً لإنشاء ملفات التحويل")
            else:
                all_files = []
                
                if selected_branch == 'all':
                    # Aggregate files from all branches
                    for branch in branches:
                        branch_folder_csv = f"transfers_from_{branch}_to_other_branches"
                        branch_folder_excel = f"transfers_excel_from_{branch}_to_other_branches"
                        branch_folder = branch_folder_csv if file_ext == ".csv" else branch_folder_excel
                        branch_path = os.path.join(directory, branch_folder)
                        
                        if os.path.exists(branch_path):
                            all_files.extend(list_output_files(branch_path, [file_ext]))
                else:
                    # Specific branch
                    branch_folder_csv = f"transfers_from_{selected_branch}_to_other_branches"
                    branch_folder_excel = f"transfers_excel_from_{selected_branch}_to_other_branches"
                    branch_folder = branch_folder_csv if file_ext == ".csv" else branch_folder_excel
                    branch_path = os.path.join(directory, branch_folder)
                    
                    if os.path.exists(branch_path):
                        all_files = list_output_files(branch_path, [file_ext])

                if not all_files:
                    if selected_branch == 'all':
                        st.warning("لا توجد ملفات تحويل لأي فرع")
                    else:
                        st.warning(f"لا توجد تحويلات من {branch_labels.get(selected_branch, selected_branch)}")
                        st.info("قد لا يكون هناك فائض في هذا الفرع للتحويل")
                else:
                    # Filter by target branch
                    # If source is 'all', we still filter by target
                    # If source is specific, we filter by target (excluding source from options)
                    
                    if selected_branch == 'all':
                        target_options = ["الكل"] + [branch_labels.get(b, b) for b in branches]
                    else:
                        target_options = ["الكل"] + [branch_labels.get(b, b) for b in branches if b != selected_branch]
                        
                    selected_target = st.selectbox(
                        "عرض التحويلات إلى:",
                        target_options,
                        key=f"target_filter_{file_ext}"
                    )
                    
                    filtered_files = []
                    if selected_target == "الكل":
                        filtered_files = all_files
                    else:
                        # Find branch key for selected target
                        target_key = None
                        for k, v in branch_labels.items():
                            if v == selected_target:
                                target_key = k
                                break
                        
                        # Filter files
                        import re
                        for f in all_files:
                            # Check if file is for target branch
                            # Pattern: from_SOURCE_to_TARGET
                            if f"to_{target_key}" in f['relative_path'] or f"to_{target_key}" in f['name']:
                                filtered_files.append(f)
                    
                    st.success(f"تم العثور على {len(filtered_files)} ملف تحويل")
                        
                    # زر تحميل الكل (للملفات المفلترة)
                    if filtered_files:
                        # Prepare files for zip with organized structure
                        zip_files = []
                        import re
                        
                        for file_info in filtered_files:
                            # Extract folder name from relative path
                            rel_path = file_info['relative_path']
                            parent_dir = os.path.dirname(rel_path)
                            
                            # Try to extract "from_X_to_Y" pattern
                            match = re.search(r'(from_[a-zA-Z0-9]+_to_[a-zA-Z0-9]+)', parent_dir)
                            if match:
                                folder_name = match.group(1)
                            else:
                                # Fallback: try to find it in filename
                                match_file = re.search(r'(from_[a-zA-Z0-9]+_to_[a-zA-Z0-9]+)', file_info['name'])
                                if match_file:
                                    folder_name = match_file.group(1)
                                else:
                                    folder_name = parent_dir if parent_dir else "other"
                            
                            # Create new file info with zip_path
                            new_info = file_info.copy()
                            new_info['zip_path'] = os.path.join(folder_name, file_info['name'])
                            zip_files.append(new_info)

                        zip_name = f"transfers_{selected_branch}_to_all_{file_ext[1:]}.zip"
                        if selected_target != "الكل":
                            zip_name = f"transfers_{selected_branch}_to_{target_key}_{file_ext[1:]}.zip"

                        zip_data = create_download_zip(zip_files, zip_name)
                        st.download_button(
                            label=f"📦 تحميل الملفات المعروضة ({len(filtered_files)})",
                            data=zip_data,
                            file_name=zip_name,
                            mime="application/zip",
                            use_container_width=True
                        )
                        st.markdown("---")
                    
                    # عرض كل ملف
                    for file_info in filtered_files:
                        with st.expander(f"📄 {file_info['name']} ({get_file_size_str(file_info['size'])})"):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                # قراءة وعرض البيانات
                                df = read_file_for_display(file_info['path'], max_rows=50)
                                if df is not None:
                                    st.dataframe(df, use_container_width=True)
                                    st.caption(f"عرض أول 50 صف (إجمالي: {len(df)} صف)")
                            
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
