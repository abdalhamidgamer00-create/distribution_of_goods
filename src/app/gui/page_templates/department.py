"""Generic department placeholder page template."""
import streamlit as st

def render_department(cfg: dict) -> None:
    """Render a department placeholder page."""
    st.set_page_config(page_title=cfg['title'], page_icon=cfg['icon'], layout="wide")
    st.title(f"{cfg['icon']} {cfg['title']}")
    st.markdown("---")
    features = '\n'.join(f"- {f}" for f in cfg['features'])
    st.info(f"**{cfg['title']}**\n\nهذا القسم مخصص لإدارة {cfg['title'].split()[-1]}.\n\n**الميزات القادمة:**\n{features}")
    if st.button("← العودة إلى الرئيسية"):
        st.switch_page("pages/00_الرئيسية.py")
