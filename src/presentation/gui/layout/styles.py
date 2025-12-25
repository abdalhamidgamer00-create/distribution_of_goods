"""Application styles orchestrator."""

import streamlit as st
from src.presentation.gui.layout.style_components.base import get_base_styles
from src.presentation.gui.layout.style_components.buttons import (
    get_button_styles
)
from src.presentation.gui.layout.style_components.containers import (
    get_container_styles
)


def apply_custom_styles() -> None:
    """Apply premium custom CSS styles by combining components."""
    css_content = f"""
    <style>
        {get_base_styles()}
        {get_button_styles()}
        {get_container_styles()}
    </style>
    """
    st.markdown(css_content, unsafe_allow_html=True)
