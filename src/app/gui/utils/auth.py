import streamlit as st
import hmac

# Default passwords (used if secrets.toml is not found)
DEFAULT_PASSWORDS = {
    "admin": "admin123",
    "user": "user123"
}


def _get_passwords() -> dict:
    """Get passwords from secrets or defaults."""
    try:
        return st.secrets["passwords"]
    except (FileNotFoundError, KeyError):
        st.warning("⚠️ استخدام كلمات المرور الافتراضية. يرجى إنشاء ملف .streamlit/secrets.toml للأمان.")
        return DEFAULT_PASSWORDS


def _verify_credentials(passwords: dict) -> bool:
    """Verify username and password."""
    return (
        st.session_state["username"] in passwords
        and hmac.compare_digest(
            st.session_state["password"],
            passwords[st.session_state["username"]],
        )
    )


def _password_entered():
    """Checks whether a password entered by the user is correct."""
    passwords = _get_passwords()
    
    if _verify_credentials(passwords):
        st.session_state["password_correct"] = True
        del st.session_state["password"]
        del st.session_state["username"]
    else:
        st.session_state["password_correct"] = False


LOGIN_STYLES = """
<style>
.stTextInput {direction: rtl;}
</style>
"""


def _render_login_inputs() -> None:
    """Render username and password inputs with login button."""
    st.markdown("### 🔐 تسجيل الدخول")
    st.text_input("اسم المستخدم", key="username")
    st.text_input("كلمة المرور", type="password", key="password")
    
    if st.button("دخول", type="primary", use_container_width=True):
        _password_entered()
        if st.session_state.get("password_correct") == False:
            st.error("😕 اسم المستخدم أو كلمة المرور غير صحيحة")
        else:
            st.rerun()


def _show_login_form():
    """Display the login form."""
    st.markdown(LOGIN_STYLES, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        _render_login_inputs()


def check_password():
    """Returns `True` if the user had a correct password."""
    if st.session_state.get("password_correct", False):
        return True
    
    _show_login_form()
    return False
