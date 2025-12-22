"""File display UI components."""

import streamlit as st

from src.app.gui.utils.file_manager import read_file_for_display, create_download_zip, get_file_size_str


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
    with st.expander(f"📄 {file_info['name']} ({get_file_size_str(file_info['size'])})"):
        content_column, download_column = st.columns([3, 1])
        
        with content_column:
            dataframe = read_file_for_display(file_info['path'], max_rows=max_rows)
            if dataframe is not None:
                st.dataframe(dataframe, use_container_width=True)
                st.caption(f"عرض أول {max_rows} صف")
        
        with download_column:
            with open(file_info['path'], 'rb') as file_handle:
                file_data = file_handle.read()
            
            st.download_button(
                label="⬇️ تحميل",
                data=file_data,
                file_name=file_info['name'],
                mime="application/octet-stream",
                key=f"{key_prefix}_{file_info['name']}_{file_ext}"
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
