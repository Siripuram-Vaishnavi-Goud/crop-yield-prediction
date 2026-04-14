"""pages/recommendation.py — Crop Recommendation Engine"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pages.helpers import load_data, SEASONS, STATES, yield_category

PALETTE = ["#1a472a", "#2d6a4f", "#52b788", "#95d5b2",
           "#d8f3dc", "#d4a017", "#b7950b", "#f0e68c"]


def render():
    st.markdown("""
    <div class="page-hero">
        <h1>💡 Crop Recommendations</h1>
        <p>Find the best-performing crops for your state, season, and conditions</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_data()

    # ── Inputs ─────────────────────────────────────────────────────────────
    st.markdown("""
    <div class='section-title'>Your Growing Conditions</div>
    <div class='section-sub'>Select your state and season to get tailored recommendations</div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        sel_state = st.selectbox("📍 State", sorted(STATES))
    with col2:
        sel_season = st.selectbox("🌦️ Season", ["Any"] + SEASONS)
    with col3:
        top_n = st.slider("Top N crops to show", 3, 15, 8)

    # ── Filter & rank ──────────────────────────────────────────────────────
    filtered = df[df["State"] == sel_state]
    if sel_season != "Any":
        filtered = filtered[filtered["Season"] == sel_season]

    if filtered.empty:
        st.warning(f"No data found for {sel_state}" +
                   (f" in {sel_season}" if sel_season != "Any" else "") + ".")
        return

    ranked = (
        filtered.groupby("Crop")
        .agg(
            Avg_Yield   = ("Yield", "mean"),
            Max_Yield   = ("Yield", "max"),
            Consistency = ("Yield", lambda x: 1 / (x.std() + 0.01)),
            Records     = ("Yield", "count"),
        )
        .reset_index()
        .sort_values("Avg_Yield", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    ranked["Rank"] = ranked.index + 1

    # ── Top recommendation card ────────────────────────────────────────────
    if not ranked.empty:
        top = ranked.iloc[0]
        label, color = yield_category(top["Avg_Yield"])
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card-green" style="display:flex; align-items:center;
             justify-content:space-between; flex-wrap:wrap; gap:1rem;">
            <div>
                <div style="color:#4a5568; font-size:0.8rem; font-weight:600;
                            text-transform:uppercase; letter-spacing:.08em;">
                    #1 Recommended Crop
                </div>
                <div style="font-family:Lora,serif; font-size:2rem;
                            font-weight:700; color:#1a472a; margin:.2rem 0;">
                    🏆 {top['Crop']}
                </div>
                <div style="color:#4a5568; font-size:0.9rem;">
                    {sel_state} · {sel_season if sel_season != 'Any' else 'All Seasons'}
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:2.2rem; font-weight:700; color:#1a472a;">
                    {top['Avg_Yield']:.3f} t/ha
                </div>
                <span class="yield-badge" style="background:{color}20;
                      color:{color}; border:1.5px solid {color}50;">
                    {label} Yield
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Rankings table + chart ─────────────────────────────────────────────
    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown("<div class='section-title' style='font-size:1rem;'>📋 Ranked Crops</div>",
                    unsafe_allow_html=True)
        display = ranked[["Rank","Crop","Avg_Yield","Max_Yield","Records"]].copy()
        display["Avg_Yield"] = display["Avg_Yield"].round(3)
        display["Max_Yield"] = display["Max_Yield"].round(3)
        display.columns = ["#", "Crop", "Avg Yield", "Max Yield", "Records"]
        st.dataframe(display, use_container_width=True, hide_index=True, height=360)

    with col2:
        st.markdown("<div class='section-title' style='font-size:1rem;'>📊 Yield Comparison</div>",
                    unsafe_allow_html=True)
        fig = px.bar(
            ranked, x="Crop", y="Avg_Yield",
            error_y=None,
            color="Avg_Yield",
            color_continuous_scale=["#d8f3dc","#1a472a"],
            labels={"Avg_Yield":"Avg Yield (t/ha)", "Crop":""},
            text=ranked["Avg_Yield"].round(2),
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=20,b=10,l=0,r=0), height=360,
            coloraxis_showscale=False,
            xaxis_tickangle=-35,
            uniformtext_minsize=8, uniformtext_mode="hide",
            font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Historical trend of top crop ───────────────────────────────────────
    if not ranked.empty:
        top_crop = ranked.iloc[0]["Crop"]
        st.markdown(f"<div class='section-title' style='font-size:1rem;'>"
                    f"📈 Historical Yield Trend — {top_crop} in {sel_state}</div>",
                    unsafe_allow_html=True)

        trend_df = df[(df["State"] == sel_state) & (df["Crop"] == top_crop)]
        if sel_season != "Any":
            trend_df = trend_df[trend_df["Season"] == sel_season]

        if not trend_df.empty:
            trend = trend_df.groupby("Crop_Year")["Yield"].mean().reset_index()
            fig2 = px.area(
                trend, x="Crop_Year", y="Yield",
                color_discrete_sequence=["#52b788"],
                labels={"Crop_Year":"Year","Yield":"Avg Yield (t/ha)"},
            )
            fig2.update_traces(
                fill='tozeroy', fillcolor='rgba(82,183,136,0.15)',
                line=dict(color="#2d6a4f", width=2.5)
            )
            fig2.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(t=10,b=10,l=0,r=0), height=240,
                font=dict(family="DM Sans"),
                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#f0f4f0"),
            )
            st.plotly_chart(fig2, use_container_width=True)

    # ── General tips ───────────────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    with st.expander("📖 How recommendations are generated"):
        st.markdown("""
        Recommendations are ranked by **average historical yield** for the selected
        state and season combination from 1997–2020 data.

        - **Avg Yield** — mean yield across all recorded years
        - **Max Yield** — highest single-year yield ever recorded
        - **Records** — how many data points exist (higher = more reliable)

        For best results, cross-reference with local agronomist advice and current
        soil/weather conditions for your specific district.
        """)