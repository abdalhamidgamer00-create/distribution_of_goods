"""Generic department placeholder page template."""
import streamlit as st

# =============================================================================
# PUBLIC API
# =============================================================================

def render_department(configuration: dict) -> None:
    """Render a department placeholder page."""
    
    st.title(f"{configuration['icon']} {configuration['title']}")
    st.markdown("---")
    
    _render_info_box(configuration)
    st.markdown("---")
    if st.button("← العودة إلى الرئيسية"):
        st.switch_page("pages/home.py")

# =============================================================================
# PRIVATE HELPERS
# =============================================================================

def _render_info_box(configuration: dict) -> None:
    """Render the main info box with features list."""
    # Extract department name (last word)
    department_name = configuration['title'].split()[-1]
    
    # Build components
    display_title = f"**{configuration['title']}**"
    description = f"هذا القسم مخصص لإدارة {department_name}."
    features_list = '\n'.join(
        f"- {feature}" for feature in configuration['features']
    )
    
    # Combine content
    content_markup = (
        f"{display_title}\n\n"
        f"{description}\n\n"
        f"**الميزات القادمة:**\n"
        f"{features_list}"
    )
    
    st.info(content_markup)

