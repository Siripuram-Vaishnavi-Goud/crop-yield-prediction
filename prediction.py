"""pages/prediction.py — Crop Yield Prediction"""

import streamlit as st
import sys, os
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pages.helpers import CROPS, SEASONS, STATES, format_yield, yield_category


def render():
    st.markdown("""
    <div class="page-hero">
        <h1>🌱 Yield Prediction</h1>
        <p>Enter your crop and field details to get an instant AI-powered yield forecast</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Model load ─────────────────────────────────────────────────────────
    model_dir = os.path.join(os.path.dirname(__file__), "..", "model")
    sys.path.insert(0, model_dir)

    try:
        from preprocess import load_artifacts, encode_input
        model, le_crop, le_season, le_state = load_artifacts()
        model_loaded = True
    except Exception as e:
        st.error(f"⚠️ Model not loaded: {e}. Please run `python model/train_model.py` first.")
        model_loaded = False
        return

    # ── Form ───────────────────────────────────────────────────────────────
    st.markdown("""
    <div class='section-title'>Input Parameters</div>
    <div class='section-sub'>Fill in all fields for an accurate prediction</div>
    """, unsafe_allow_html=True)

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🌾 Crop Details**")
            crop   = st.selectbox("Crop Type", sorted(CROPS))
            season = st.selectbox("Season", SEASONS)
            state  = st.selectbox("State", sorted(STATES))
            year   = st.number_input("Crop Year", min_value=1997, max_value=2030,
                                     value=2024, step=1)

        with col2:
            st.markdown("**🌍 Field & Environmental Details**")
            area      = st.number_input("Area (hectares)",       min_value=1.0,    value=1000.0,  step=100.0)
            rainfall  = st.number_input("Annual Rainfall (mm)",  min_value=100.0,  value=1200.0,  step=50.0)
            fertilizer = st.number_input("Fertilizer used (kg)", min_value=0.0,    value=100000.0, step=1000.0)
            pesticide  = st.number_input("Pesticide used (kg)",  min_value=0.0,    value=500.0,   step=10.0)

        submitted = st.form_submit_button("🔮  Predict Yield", use_container_width=True)

    # ── Result ─────────────────────────────────────────────────────────────
    if submitted and model_loaded:
        try:
            enc_crop, enc_season, enc_state = encode_input(
                crop, season, state, le_crop, le_season, le_state
            )
            import pandas as pd
            features = pd.DataFrame([[
                enc_crop, year, enc_season, enc_state,
                area, rainfall, fertilizer, pesticide
            ]], columns=["Crop","Crop_Year","Season","State",
                         "Area","Annual_Rainfall","Fertilizer","Pesticide"])
            prediction = float(model.predict(features)[0])
            label, color = yield_category(prediction)

            st.markdown("<br/>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="card-green" style="text-align:center; padding:2.5rem;">
                <div style="color:#4a5568; font-size:0.85rem; font-weight:600;
                            text-transform:uppercase; letter-spacing:0.1em; margin-bottom:.5rem;">
                    Predicted Yield
                </div>
                <div style="font-family:Lora,serif; font-size:3rem; font-weight:700;
                            color:#1a472a; line-height:1.1;">
                    {format_yield(prediction)}
                </div>
                <div style="margin-top:1rem;">
                    <span class="yield-badge" style="background:{color}20; color:{color};
                          border:1.5px solid {color}50;">
                        {label} Yield
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Input summary
            st.markdown("<br/>", unsafe_allow_html=True)
            st.markdown("<div class='section-title' style='font-size:1rem;'>📋 Input Summary</div>",
                        unsafe_allow_html=True)
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("Crop",     crop)
            sc2.metric("Season",   season)
            sc3.metric("State",    state)
            sc4.metric("Year",     str(year))
            sc5, sc6, sc7, sc8 = st.columns(4)
            sc5.metric("Area",      f"{area:,.0f} ha")
            sc6.metric("Rainfall",  f"{rainfall:.0f} mm")
            sc7.metric("Fertilizer", f"{fertilizer:,.0f} kg")
            sc8.metric("Pesticide",  f"{pesticide:,.0f} kg")

        except ValueError as e:
            st.error(f"⚠️ Encoding error: {e}")
        except Exception as e:
            st.error(f"⚠️ Prediction failed: {e}")

    # ── Tips ───────────────────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    with st.expander("💡 Tips for Better Predictions"):
        st.markdown("""
        - **Area**: Enter the total cultivated area in hectares for this crop/season.
        - **Annual Rainfall**: Use district-level average. 1000–2000 mm is typical for most of India.
        - **Fertilizer**: Total kg of all fertilizers applied (NPK combined).
        - **Pesticide**: Total kg of all pesticide applications for the season.
        - The model was trained on data from 1997–2020; predictions for future years extrapolate trends.
        """)