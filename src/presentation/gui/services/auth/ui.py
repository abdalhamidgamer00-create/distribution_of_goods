"""Authentication UI logic."""

import streamlit as st
from src.presentation.gui.services.auth.session import handle_password_entry

LOGIN_STYLES = """
<style>
    /* Hide sidebar on login page */
    [data-testid="stSidebar"] {
        display: none;
    }
    
    /* Center and style login card */
    .stTextInput { 
        direction: rtl; 
    }
    
    div[data-testid="stColumn"] {
        background: rgba(255, 255, 255, 0.8);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
    }
</style>
"""

def render_login_inputs() -> None:
    """Render username and password inputs with login button."""
    st.markdown("### 🔐 تسجيل الدخول")
    
    st.text_input("اسم المستخدم", key="username")
    st.text_input("كلمة المرور", type="password", key="password")
    
    if st.button("دخول", type="primary", use_container_width=True):
        handle_password_entry()
        _check_login_status()


def _check_login_status() -> None:
    """Check login status and show error or rerun."""
    if st.session_state.get("password_correct") is False:
        st.error("😕 اسم المستخدم أو كلمة المرور غير صحيحة")
    else:
        st.rerun()


def show_login_form() -> None:
    """Display the login form."""
    st.markdown(LOGIN_STYLES, unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        render_login_inputs()
