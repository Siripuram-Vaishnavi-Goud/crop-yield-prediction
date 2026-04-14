"""pages/home.py — Landing page"""

import streamlit as st


def render():
    # ── Hero ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="page-hero">
        <h1>🌾 CropSight</h1>
        <p>AI-powered crop yield prediction for smarter agricultural decisions across India</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Stats row ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Crop Varieties", "55", help="Unique crops in dataset")
    with c2:
        st.metric("States Covered", "30", help="Indian states & UTs")
    with c3:
        st.metric("Years of Data", "24", "1997 – 2020")
    with c4:
        st.metric("Model Accuracy", "90.8%", "R² score")

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Feature cards ──────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-title">What CropSight Offers</div>
    <div class="section-sub">Everything you need to make data-driven farming decisions</div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="card">
            <div style="font-size:2rem; margin-bottom:.75rem;">📊</div>
            <div style="font-weight:700; font-size:1.05rem; color:#1a472a; margin-bottom:.5rem;">
                Dashboard
            </div>
            <div style="color:#718096; font-size:0.9rem; line-height:1.6;">
                Visual overview of crop performance trends, state-wise production,
                and year-on-year yield changes. Requires login.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="card">
            <div style="font-size:2rem; margin-bottom:.75rem;">🌱</div>
            <div style="font-weight:700; font-size:1.05rem; color:#1a472a; margin-bottom:.5rem;">
                Yield Prediction
            </div>
            <div style="color:#718096; font-size:0.9rem; line-height:1.6;">
                Enter your crop details — season, state, rainfall, fertilizer —
                and get an instant AI-powered yield forecast.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="card">
            <div style="font-size:2rem; margin-bottom:.75rem;">💡</div>
            <div style="font-weight:700; font-size:1.05rem; color:#1a472a; margin-bottom:.5rem;">
                Recommendations
            </div>
            <div style="color:#718096; font-size:0.9rem; line-height:1.6;">
                Get the top-performing crops for your state and season based on
                historical yield data analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("""
        <div class="card">
            <div style="font-size:2rem; margin-bottom:.75rem;">🔍</div>
            <div style="font-weight:700; font-size:1.05rem; color:#1a472a; margin-bottom:.5rem;">
                Dataset Analysis
            </div>
            <div style="color:#718096; font-size:0.9rem; line-height:1.6;">
                Explore 19,000+ records with interactive filters, correlation heatmaps,
                and distribution plots.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="card">
            <div style="font-size:2rem; margin-bottom:.75rem;">🤖</div>
            <div style="font-weight:700; font-size:1.05rem; color:#1a472a; margin-bottom:.5rem;">
                Random Forest Model
            </div>
            <div style="color:#718096; font-size:0.9rem; line-height:1.6;">
                Upgraded from Decision Tree to Random Forest with 200 estimators,
                achieving 90.8% R² accuracy.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown("""
        <div class="card">
            <div style="font-size:2rem; margin-bottom:.75rem;">🔐</div>
            <div style="font-weight:700; font-size:1.05rem; color:#1a472a; margin-bottom:.5rem;">
                Secure Auth
            </div>
            <div style="color:#718096; font-size:0.9rem; line-height:1.6;">
                Local SQLite-backed user accounts with hashed passwords.
                Register in seconds, login to unlock the dashboard.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── CTA ────────────────────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("""
    <div class="card-green" style="text-align:center; padding: 2.5rem;">
        <div style="font-family:Lora,serif; font-size:1.4rem; font-weight:600;
                    color:#1a472a; margin-bottom:.5rem;">
            Ready to predict your crop yield?
        </div>
        <div style="color:#4a5568; font-size:0.9rem; margin-bottom:1.5rem;">
            Use the sidebar to navigate to the Prediction page — no login required.
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 1, 2])
    with c2:
        if st.button("🌱  Try Prediction", use_container_width=True):
            st.session_state.page = "prediction"
            st.rerun()