"""pages/dashboard.py — Analytics Dashboard (login required)"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pages.helpers import load_data


PALETTE = ["#1a472a", "#2d6a4f", "#52b788", "#95d5b2", "#d8f3dc", "#d4a017"]


def render():
    st.markdown("""
    <div class="page-hero">
        <h1>📊 Dashboard</h1>
        <p>Comprehensive overview of Indian crop yield trends (1997–2020)</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_data()

    # ── KPI Row ────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Total Records",    f"{len(df):,}")
    with c2: st.metric("Crops",            df["Crop"].nunique())
    with c3: st.metric("States",           df["State"].nunique())
    with c4: st.metric("Avg Yield",        f"{df['Yield'].mean():.2f} t/ha")
    with c5: st.metric("Max Yield",        f"{df['Yield'].max():.1f} t/ha")

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Filters ────────────────────────────────────────────────────────────
    with st.expander("🔧 Filters", expanded=False):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            states = ["All"] + sorted(df["State"].unique())
            sel_state = st.selectbox("State", states)
        with fc2:
            crops = ["All"] + sorted(df["Crop"].unique())
            sel_crop = st.selectbox("Crop", crops)
        with fc3:
            yr_min, yr_max = int(df["Crop_Year"].min()), int(df["Crop_Year"].max())
            yr_range = st.slider("Year Range", yr_min, yr_max, (yr_min, yr_max))

    dff = df.copy()
    if sel_state != "All":
        dff = dff[dff["State"] == sel_state]
    if sel_crop != "All":
        dff = dff[dff["Crop"] == sel_crop]
    dff = dff[(dff["Crop_Year"] >= yr_range[0]) & (dff["Crop_Year"] <= yr_range[1])]

    # ── Row 1: Yield over time + Top crops ─────────────────────────────────
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("<div class='section-title' style='font-size:1.1rem;'>📈 Average Yield Over Time</div>",
                    unsafe_allow_html=True)
        yearly = dff.groupby("Crop_Year")["Yield"].mean().reset_index()
        fig = px.area(
            yearly, x="Crop_Year", y="Yield",
            color_discrete_sequence=["#52b788"],
            labels={"Crop_Year": "Year", "Yield": "Avg Yield (t/ha)"},
        )
        fig.update_traces(
            fill='tozeroy',
            fillcolor='rgba(82,183,136,0.15)',
            line=dict(color="#2d6a4f", width=2.5),
        )
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=10, b=10, l=0, r=0),
            height=300,
            xaxis=dict(showgrid=False, linecolor="#e2e8f0"),
            yaxis=dict(gridcolor="#f0f4f0", linecolor="#e2e8f0"),
            font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("<div class='section-title' style='font-size:1.1rem;'>🏆 Top 10 Crops by Yield</div>",
                    unsafe_allow_html=True)
        top_crops = (
            dff.groupby("Crop")["Yield"].mean()
            .sort_values(ascending=False).head(10).reset_index()
        )
        fig2 = px.bar(
            top_crops, x="Yield", y="Crop", orientation="h",
            color="Yield", color_continuous_scale=["#d8f3dc", "#1a472a"],
            labels={"Yield": "Avg Yield (t/ha)", "Crop": ""},
        )
        fig2.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=10, b=10, l=0, r=0),
            height=300, showlegend=False,
            coloraxis_showscale=False,
            yaxis=dict(autorange="reversed"),
            font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 2: State map choropleth + Season breakdown ──────────────────────
    col3, col4 = st.columns([3, 2])

    with col3:
        st.markdown("<div class='section-title' style='font-size:1.1rem;'>🗺️ State-wise Average Yield</div>",
                    unsafe_allow_html=True)
        state_yield = dff.groupby("State")["Yield"].mean().reset_index()
        fig3 = px.bar(
            state_yield.sort_values("Yield", ascending=False),
            x="State", y="Yield",
            color="Yield", color_continuous_scale=["#d8f3dc", "#1a472a"],
            labels={"Yield": "Avg Yield (t/ha)", "State": ""},
        )
        fig3.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=10, b=10, l=0, r=0),
            height=300, showlegend=False,
            coloraxis_showscale=False,
            xaxis=dict(tickangle=-45),
            font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown("<div class='section-title' style='font-size:1.1rem;'>🌦️ Yield by Season</div>",
                    unsafe_allow_html=True)
        season_yield = dff.groupby("Season")["Yield"].mean().reset_index()
        fig4 = px.pie(
            season_yield, names="Season", values="Yield",
            color_discrete_sequence=PALETTE,
            hole=0.45,
        )
        fig4.update_traces(textposition='outside', textinfo='label+percent')
        fig4.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=10, b=10, l=0, r=0),
            height=300, showlegend=False,
            font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig4, use_container_width=True)

    # ── Row 3: Correlation + Distribution ──────────────────────────────────
    col5, col6 = st.columns(2)

    with col5:
        st.markdown("<div class='section-title' style='font-size:1.1rem;'>🔗 Feature Correlation</div>",
                    unsafe_allow_html=True)
        num_cols = ["Area", "Annual_Rainfall", "Fertilizer", "Pesticide", "Yield"]
        corr = dff[num_cols].corr()
        fig5 = px.imshow(
            corr, text_auto=".2f", aspect="auto",
            color_continuous_scale=["#ffffff", "#52b788", "#1a472a"],
            zmin=-1, zmax=1,
        )
        fig5.update_layout(
            margin=dict(t=10, b=10, l=0, r=0), height=280,
            font=dict(family="DM Sans"),
            paper_bgcolor="white",
        )
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        st.markdown("<div class='section-title' style='font-size:1.1rem;'>📉 Yield Distribution</div>",
                    unsafe_allow_html=True)
        # Cap at 99th percentile for readability
        yield_cap = dff["Yield"].quantile(0.99)
        fig6 = px.histogram(
            dff[dff["Yield"] <= yield_cap], x="Yield", nbins=60,
            color_discrete_sequence=["#52b788"],
            labels={"Yield": "Yield (t/ha)", "count": "Records"},
        )
        fig6.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(t=10, b=10, l=0, r=0), height=280,
            bargap=0.05,
            font=dict(family="DM Sans"),
            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#f0f4f0"),
        )
        st.plotly_chart(fig6, use_container_width=True)

    # ── Raw data preview ───────────────────────────────────────────────────
    with st.expander("📋 Raw Data Preview"):
        st.dataframe(
            dff.head(200).style.background_gradient(
                subset=["Yield"], cmap="Greens"
            ),
            use_container_width=True, height=300,
        )
        st.caption(f"Showing first 200 of {len(dff):,} filtered rows.")