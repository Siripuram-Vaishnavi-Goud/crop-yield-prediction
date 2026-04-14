"""pages/contact.py — Contact page"""

import streamlit as st


def render():
    st.markdown("""
    <div class="page-hero">
        <h1>✉️ Contact Us</h1>
        <p>Have questions or feedback? We'd love to hear from you.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("""
        <div class='section-title'>Send a Message</div>
        <div class='section-sub'>Fill out the form and we'll get back to you soon</div>
        """, unsafe_allow_html=True)

        name    = st.text_input("Full Name",     placeholder="Your name")
        email   = st.text_input("Email Address", placeholder="your@email.com")
        subject = st.selectbox("Subject", [
            "General Inquiry",
            "Model Feedback",
            "Data Issue / Bug Report",
            "Feature Request",
            "Partnership",
            "Other",
        ])
        message = st.text_area("Message", placeholder="Write your message here...", height=180)

        if st.button("📨 Send Message", use_container_width=False):
            if not name or not email or not message:
                st.error("Please fill in Name, Email, and Message.")
            elif "@" not in email:
                st.error("Please enter a valid email address.")
            else:
                st.success(
                    f"✅ Thank you, {name}! Your message has been received. "
                    "We'll respond within 2–3 business days."
                )

    with col2:
        st.markdown("""
        <div class='section-title'>Contact Info</div>
        <div class='section-sub'>Other ways to reach us</div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card" style="margin-bottom:1rem;">
            <div style="font-size:1.4rem; margin-bottom:.5rem;">📧</div>
            <div style="font-weight:600; color:#1a472a; margin-bottom:.2rem;">Email</div>
            <div style="color:#718096; font-size:0.9rem;">support@cropsight.ai</div>
        </div>
        <div class="card" style="margin-bottom:1rem;">
            <div style="font-size:1.4rem; margin-bottom:.5rem;">🐙</div>
            <div style="font-weight:600; color:#1a472a; margin-bottom:.2rem;">GitHub</div>
            <div style="color:#718096; font-size:0.9rem;">github.com/cropsight</div>
        </div>
        <div class="card">
            <div style="font-size:1.4rem; margin-bottom:.5rem;">📍</div>
            <div style="font-weight:600; color:#1a472a; margin-bottom:.2rem;">Location</div>
            <div style="color:#718096; font-size:0.9rem;">India 🇮🇳</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="card-green" style="margin-top:1rem;">
            <div style="font-weight:600; color:#1a472a; margin-bottom:.5rem;">About CropSight</div>
            <div style="color:#4a5568; font-size:0.88rem; line-height:1.6;">
                CropSight is a data-driven crop yield prediction platform built
                with ❤️ for Indian agriculture. We use machine learning on 24 years
                of ICAR data to help farmers and researchers make smarter decisions.
            </div>
        </div>
        """, unsafe_allow_html=True)