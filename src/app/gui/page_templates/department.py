"""Generic department placeholder page template."""
import streamlit as st


# =============================================================================
# PUBLIC API
# =============================================================================

def render_department(cfg: dict) -> None:
    """Render a department placeholder page."""
    st.set_page_config(
        page_title=cfg['title'],
        page_icon=cfg['icon'],
        layout="wide"
    )
    
    st.title(f"{cfg['icon']} {cfg['title']}")
    st.markdown("---")
    
    _render_info_box(cfg)
    
    if st.button("← العودة إلى الرئيسية"):
        st.switch_page("pages/00_الرئيسية.py")


# =============================================================================
# PRIVATE HELPERS
# =============================================================================

def _render_info_box(cfg: dict) -> None:
    """Render the main info box with features list."""
    # Extract department name (last word)
    dept_name = cfg['title'].split()[-1]
    
    # Build components
    title = f"**{cfg['title']}**"
    desc = f"هذا القسم مخصص لإدارة {dept_name}."
    features_list = '\n'.join(f"- {f}" for f in cfg['features'])
    
    # Combine content
    content = (
        f"{title}\n\n"
        f"{desc}\n\n"
        f"**الميزات القادمة:**\n"
        f"{features_list}"
    )
    
    st.info(content)
