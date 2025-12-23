"""File display UI components."""
import streamlit as st
from src.app.gui.utils.file_manager import (
    read_file_for_display,
    create_download_zip,
    get_file_size_str
)


# =============================================================================
# PUBLIC API
# =============================================================================

def render_file_expander(
    file_info: dict,
    file_ext: str,
    key_prefix: str = "download",
    max_rows: int = 50
) -> None:
    """Render file expander with dataframe preview and download button."""
    size_str = get_file_size_str(file_info['size'])
    expander_label = f"📄 {file_info['name']} ({size_str})"
    
    with st.expander(expander_label):
        content_column, download_column = st.columns([3, 1])
        
        with content_column:
            _render_file_preview(file_info, max_rows)
        
        with download_column:
            _render_download_button(
                file_info,
                file_ext,
                key_prefix
            )


def render_download_all_button(
    files: list,
    zip_name: str,
    label_template: str = "📦 تحميل الملفات المعروضة ({count})",
    add_separator: bool = True
) -> None:
    """Render download all button for a list of files."""
    if not files:
        return
    
    zip_data = create_download_zip(files, zip_name)
    
    st.download_button(
        label=label_template.format(count=len(files)),
        data=zip_data,
        file_name=zip_name,
        mime="application/zip",
        use_container_width=True
    )
    
    if add_separator:
        st.markdown("---")


# =============================================================================
# PRIVATE HELPERS
# =============================================================================

def _render_file_preview(file_info: dict, max_rows: int) -> None:
    """Render dataframe preview in the expander."""
    dataframe = read_file_for_display(
        file_info['path'], 
        max_rows=max_rows
    )
    
    if dataframe is not None:
        st.dataframe(dataframe, use_container_width=True)
        st.caption(f"عرض أول {max_rows} صف")


def _render_download_button(
    file_info: dict,
    file_ext: str, 
    key_prefix: str
) -> None:
    """Render the individual file download button."""
    with open(file_info['path'], 'rb') as file_handle:
        file_data = file_handle.read()
    
    key = f"{key_prefix}_{file_info['name']}_{file_ext}"
    
    st.download_button(
        label="⬇️ تحميل",
        data=file_data,
        file_name=file_info['name'],
        mime="application/octet-stream",
        key=key
    )
