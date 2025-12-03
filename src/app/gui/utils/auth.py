import streamlit as st
import hmac

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and hmac.compare_digest(
                st.session_state["password"],
                st.secrets["passwords"][st.session_state["username"]],
            )
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username and password
    st.markdown(
        """
        <style>
        .stTextInput {direction: rtl;}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 تسجيل الدخول")
        st.text_input("اسم المستخدم", key="username")
        st.text_input("كلمة المرور", type="password", key="password")
        
        if st.button("دخول", type="primary", use_container_width=True):
            password_entered()
            if st.session_state.get("password_correct") == False:
                st.error("😕 اسم المستخدم أو كلمة المرور غير صحيحة")
            else:
                st.rerun()

    return False
