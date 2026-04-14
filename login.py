"""pages/login.py"""
import streamlit as st
from pages.auth import login_user

def render():
    st.markdown("""
    <style>
    .block-container{padding-top:2rem!important;}
    .stButton>button{width:100%;}
    </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("<div style='text-align:center;font-size:2.5rem;'>🌾</div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;color:#1a472a;font-family:Lora,serif;margin:.25rem 0 .1rem;'>Welcome Back</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#718096;font-size:.9rem;margin-bottom:1.5rem;'>Sign in to your CropSight account</p>", unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter your username", key="lp_user")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="lp_pass")

        c1, c2 = st.columns(2)
        with c1:
            st.checkbox("Remember me", value=True, key="lp_remember")
        with c2:
            st.markdown("<div style='text-align:right;padding-top:.35rem;color:#52b788;font-size:.85rem;font-weight:500;'>Forgot password?</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

        if st.button("Sign In →", use_container_width=True, key="lp_signin"):
            if not username or not password:
                st.error("Please enter both username and password.")
            else:
                ok, msg = login_user(username, password)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.username = msg
                    st.session_state.page = "dashboard"
                    st.success(f"Welcome back, {msg}! 🎉")
                    st.rerun()
                else:
                    st.error(f"⚠️ {msg}")

        st.markdown("<div style='text-align:center;color:#a0aec0;font-size:.82rem;margin:.9rem 0;'>— or —</div>", unsafe_allow_html=True)

        if st.button("🔍 Explore Without Login", use_container_width=True, key="lp_guest"):
            st.session_state.page = "prediction"
            st.rerun()

        st.markdown("<div style='text-align:center;color:#718096;font-size:.87rem;margin-top:1rem;'>Don't have an account?</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:.3rem'></div>", unsafe_allow_html=True)

        if st.button("Create Free Account", use_container_width=True, key="lp_register"):
            st.session_state.page = "register"
            st.rerun()