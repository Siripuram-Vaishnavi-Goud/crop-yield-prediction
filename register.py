"""pages/register.py"""
import streamlit as st
from pages.auth import register_user


def pw_strength(pw):
    score = sum([
        len(pw) >= 8,
        any(c.isupper() for c in pw),
        any(c.isdigit() for c in pw),
        any(c in "!@#$%^&*()" for c in pw)
    ])
    labels = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"]
    colors = ["#e74c3c",   "#e67e22", "#f1c40f", "#2ecc71", "#1a9e50"]
    return score, labels[score], colors[score]


def render():
    st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.6, 1])

    with col:
        # Header
        st.markdown("<div style='text-align:center;font-size:2.5rem;'>&#127807;</div>",
                    unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center;color:#1a472a;font-family:Lora,serif;"
                    "margin:.25rem 0 .1rem;'>Create Account</h2>",
                    unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#718096;font-size:.9rem;"
                    "margin-bottom:1.5rem;'>Join CropSight and start predicting crop yields</p>",
                    unsafe_allow_html=True)

        # Username + Email
        c1, c2 = st.columns(2)
        with c1:
            username = st.text_input("Username", placeholder="e.g. farmer_ravi",
                                     key="rp_user")
        with c2:
            email = st.text_input("Email", placeholder="you@email.com",
                                  key="rp_email")

        # Password
        password = st.text_input("Password", type="password",
                                 placeholder="Min. 6 characters", key="rp_pass")

        # Password strength bar
        if password:
            score, label, color = pw_strength(password)
            pct = int((score / 4) * 100)
            st.markdown(f"""
            <div style='height:6px;border-radius:3px;background:#e2e8f0;
                        margin:.3rem 0 .15rem;overflow:hidden;'>
                <div style='height:100%;width:{pct}%;background:{color};
                            border-radius:3px;'></div>
            </div>
            <div style='font-size:.78rem;color:{color};font-weight:600;
                        margin-bottom:.3rem;'>Strength: {label}</div>
            """, unsafe_allow_html=True)

        # Confirm password
        confirm = st.text_input("Confirm Password", type="password",
                                placeholder="Repeat your password", key="rp_confirm")

        # Match indicator
        if confirm:
            if password == confirm:
                st.markdown("<div style='color:#2ecc71;font-size:.8rem;"
                            "font-weight:600;margin:.1rem 0 .3rem;'>"
                            "&#10003; Passwords match</div>",
                            unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:#e74c3c;font-size:.8rem;"
                            "font-weight:600;margin:.1rem 0 .3rem;'>"
                            "&#10007; Passwords do not match</div>",
                            unsafe_allow_html=True)

        # Terms checkbox
        agree = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy",
            key="rp_terms"
        )

        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)

        # Validation and submit
        if st.button("Create My Account", use_container_width=True, key="rp_create"):
            # Run all validations and show ONE clear error
            if not username:
                st.error("Please enter a username.")
            elif len(username) < 3:
                st.error("Username must be at least 3 characters.")
            elif not email:
                st.error("Please enter your email address.")
            elif "@" not in email or "." not in email.split("@")[-1]:
                st.error("Please enter a valid email address.")
            elif not password:
                st.error("Please enter a password.")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters.")
            elif not confirm:
                st.error("Please confirm your password.")
            elif password != confirm:
                st.error("Passwords do not match. Please re-enter.")
            elif not agree:
                st.error("Please agree to the Terms of Service to continue.")
            else:
                with st.spinner("Creating your account..."):
                    ok, msg = register_user(username, email, password)
                if ok:
                    st.success(f"Account created! Welcome, {username}! Redirecting to login...")
                    st.balloons()
                    import time; time.sleep(1.5)
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(f"{msg}")

        st.markdown("<div style='text-align:center;color:#a0aec0;font-size:.75rem;"
                    "margin:.75rem 0 .5rem;'>"
                    "Your data is stored locally and never shared.</div>",
                    unsafe_allow_html=True)

        st.markdown("<div style='text-align:center;color:#718096;font-size:.87rem;"
                    "margin-bottom:.3rem;'>Already have an account?</div>",
                    unsafe_allow_html=True)

        if st.button("Sign In Instead", use_container_width=True, key="rp_login"):
            st.session_state.page = "login"
            st.rerun()