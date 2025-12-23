"""Application styles."""

import streamlit as st


def apply_custom_styles() -> None:
    """Apply custom CSS styles."""
    styles = """
    <style>
        .main { direction: rtl; text-align: right; }
        .stButton>button { width: 100%; }
        h1, h2, h3 { text-align: right; }
    </style>
    """
    st.markdown(styles, unsafe_allow_html=True)
