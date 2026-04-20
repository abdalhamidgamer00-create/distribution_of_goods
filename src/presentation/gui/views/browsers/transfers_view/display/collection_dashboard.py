"""Logic for displaying unified collection dashboards."""
import streamlit as st
from typing import List, Dict
from src.presentation.gui.components import (
    render_file_expander,
    render_download_all_button
)
from src.presentation.gui.utils.display_utils import prepare_zip_paths

def display_unified_collection_files(
    artifact_list: List[Dict],
    interaction_key_prefix: str,
    target_branch: str,
    file_extension: str
) -> None:
    """Display all collection files in a single unified section."""
    
    st.markdown(f"### 📦 التقارير المجمعة لفرع {target_branch}")
    st.info("💡 تم تجميع كافة التقارير في قسم واحد لسهولة الوصول.")
    
    metric_column_1, metric_column_2 = st.columns(2)
    metric_column_1.metric("إجمالي التقارير", len(artifact_list))
    
    branch_display_name = (target_branch or "عام").title()
    metric_column_2.metric("فرع المصدر", branch_display_name)
    st.markdown("---")

    if not artifact_list:
        st.warning("⚠️ لا توجد ملفات متوفرة حالياً.")
        return

    prepare_zip_paths(artifact_list, path_strategy='transfer')
    zip_name = f"all_collections_{target_branch}_{file_extension[1:]}.zip"
    
    render_download_all_button(
        artifact_list, 
        zip_name,
        label_template="📥 تحميل كافة التقارير المجمعة ({count})",
        key=f"{interaction_key_prefix}_unified_download_{file_extension}"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📄 قائمة الملفات")
    
    for index, file_information in enumerate(artifact_list):
        render_file_expander(
            file_information, 
            file_extension,
            key_prefix=f"{interaction_key_prefix}_unified_list_"
                       f"{index}_{file_extension}"
        )
