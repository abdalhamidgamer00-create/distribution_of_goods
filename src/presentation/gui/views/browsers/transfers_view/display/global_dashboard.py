"""Logic for displaying global multi-branch tabbed dashboards."""
import streamlit as st
from typing import List, Dict
from src.presentation.gui.components import render_download_all_button
from src.presentation.gui.utils.translations import BRANCH_NAMES
from src.presentation.gui.utils.display_utils import prepare_zip_paths
from src.presentation.gui.views.browsers.transfers_view.display.collection_dashboard import (
    display_unified_collection_files
)

def display_global_collection_dashboard(
    grouped_artifacts: Dict[str, List[Dict]],
    complete_artifact_list: List[Dict],
    interaction_key_prefix: str,
    file_extension: str
) -> None:
    """Display collection files organized by branch using tabs."""
    st.info(
        f"📂 عرض كلي لجميع الفروع - "
        f"({len(complete_artifact_list)} ملف مجمع)"
    )
    
    prepare_zip_paths(complete_artifact_list, path_strategy='transfer')
    zip_name = (
        f"complete_network_collections_{file_extension[1:]}.zip"
    )
    
    render_download_all_button(
        complete_artifact_list, 
        zip_name,
        label_template="📦 تحميل كافة تقارير جميع الفروع ({count})",
        key=f"{interaction_key_prefix}_global_bulk_download_{file_extension}"
    )
    
    st.markdown("---")
    
    branch_keys = sorted(
        grouped_artifacts.keys(), 
        key=lambda key: str(key) if key is not None else ""
    )
    
    tab_labels = [
        str(BRANCH_NAMES.get(k, k)) if k is not None else "🌐 تقارير عامة" 
        for k in branch_keys
    ]
    
    if not branch_keys:
        st.warning("⚠️ لا توجد بيانات متاحة لأي فرع.")
        return
        
    branch_tabs = st.tabs(tab_labels)
    for branch_key, tab_interface in zip(branch_keys, branch_tabs):
        with tab_interface:
            display_unified_collection_files(
                grouped_artifacts[branch_key],
                f"{interaction_key_prefix}_{branch_key}",
                branch_key,
                file_extension
            )
 Riverside
