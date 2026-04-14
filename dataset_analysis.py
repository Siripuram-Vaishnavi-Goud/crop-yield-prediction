"""pages/dataset_analysis.py — Dataset Exploration"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pages.helpers import load_data

PALETTE = ["#1a472a", "#2d6a4f", "#52b788", "#95d5b2", "#d8f3dc",
           "#d4a017", "#b7950b", "#f0e68c"]


def render():
    st.markdown("""
    <div class="page-hero">
        <h1>🔍 Dataset Analysis</h1>
        <p>Explore 19,000+ crop yield records with interactive charts and filters</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_data()

    tabs = st.tabs(["📊 Overview", "🌾 Crop Analysis", "🗺️ State Analysis",
                    "🌦️ Season Trends", "📋 Raw Data"])

    # ── TAB 1: Overview ────────────────────────────────────────────────────
    with tabs[0]:
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Total Records",  f"{len(df):,}")
        with c2: st.metric("Unique Crops",   df["Crop"].nunique())
        with c3: st.metric("States",         df["State"].nunique())
        with c4: st.metric("Year Span",      f"{int(df['Crop_Year'].min())}–{int(df['Crop_Year'].max())}")

        st.markdown("<br/>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Numeric Summary**")
            st.dataframe(
                df[["Area","Annual_Rainfall","Fertilizer","Pesticide","Yield"]]
                .describe().round(2),
                use_container_width=True,
            )
        with col2:
            st.markdown("**Records per Season**")
            sc = df["Season"].value_counts().reset_index()
            sc.columns = ["Season", "Count"]
            fig = px.bar(sc, x="Season", y="Count",
                         color="Count", color_continuous_scale=["#d8f3dc","#1a472a"])
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(t=10,b=10,l=0,r=0), height=280,
                coloraxis_showscale=False, showlegend=False,
                font=dict(family="DM Sans"),
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── TAB 2: Crop Analysis ───────────────────────────────────────────────
    with tabs[1]:
        col1, col2 = st.columns([1, 3])
        with col1:
            top_n = st.slider("Show top N crops", 5, 30, 15)
            metric = st.radio("By", ["Mean Yield", "Median Yield", "Max Yield"])

        agg = {"Mean Yield": "mean", "Median Yield": "median", "Max Yield": "max"}[metric]
        crop_stats = (
            df.groupby("Crop")["Yield"]
            .agg(agg).sort_values(ascending=False)
            .head(top_n).reset_index()
        )
        crop_stats.columns = ["Crop", "Yield"]

        with col2:
            fig = px.bar(
                crop_stats, x="Crop", y="Yield",
                color="Yield", color_continuous_scale=["#d8f3dc", "#1a472a"],
                labels={"Yield": f"{metric} (t/ha)"},
            )
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(t=30,b=10,l=0,r=0), height=360,
                coloraxis_showscale=False, xaxis_tickangle=-40,
                font=dict(family="DM Sans"),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Yield distribution for selected crop
        st.markdown("**Deep Dive: Yield distribution for a specific crop**")
        sel_crop = st.selectbox("Select Crop", sorted(df["Crop"].unique()))
        crop_df = df[df["Crop"] == sel_crop]

        c1, c2 = st.columns(2)
        with c1:
            cap = crop_df["Yield"].quantile(0.99)
            fig2 = px.histogram(
                crop_df[crop_df["Yield"] <= cap], x="Yield", nbins=40,
                color_discrete_sequence=["#52b788"],
                title=f"Yield distribution — {sel_crop}",
            )
            fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                               margin=dict(t=40,b=10), height=280,
                               font=dict(family="DM Sans"))
            st.plotly_chart(fig2, use_container_width=True)
        with c2:
            yearly_crop = crop_df.groupby("Crop_Year")["Yield"].mean().reset_index()
            fig3 = px.line(yearly_crop, x="Crop_Year", y="Yield",
                           markers=True, title=f"Avg yield over years — {sel_crop}",
                           color_discrete_sequence=["#2d6a4f"])
            fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                               margin=dict(t=40,b=10), height=280,
                               font=dict(family="DM Sans"))
            st.plotly_chart(fig3, use_container_width=True)

    # ── TAB 3: State Analysis ──────────────────────────────────────────────
    with tabs[2]:
        state_stats = df.groupby("State").agg(
            Avg_Yield=("Yield", "mean"),
            Records=("Yield", "count"),
            Crops=("Crop", "nunique"),
        ).reset_index().sort_values("Avg_Yield", ascending=False)

        col1, col2 = st.columns([3, 2])
        with col1:
            fig = px.bar(
                state_stats, x="State", y="Avg_Yield",
                color="Avg_Yield", color_continuous_scale=["#d8f3dc","#1a472a"],
                labels={"Avg_Yield": "Avg Yield (t/ha)", "State": ""},
                title="Average Yield by State",
            )
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(t=40,b=10,l=0,r=0), height=380,
                coloraxis_showscale=False, xaxis_tickangle=-45,
                font=dict(family="DM Sans"),
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.markdown("**State Summary Table**")
            st.dataframe(
                state_stats.rename(columns={
                    "State": "State", "Avg_Yield": "Avg Yield",
                    "Records": "Records", "Crops": "Crops"
                }).round(3),
                use_container_width=True, height=380,
            )

        # State deep dive
        st.markdown("**Top crops in a state**")
        sel_state = st.selectbox("Select State", sorted(df["State"].unique()))
        state_df  = df[df["State"] == sel_state]
        top_state = (
            state_df.groupby("Crop")["Yield"].mean()
            .sort_values(ascending=False).head(12).reset_index()
        )
        fig2 = px.bar(
            top_state, x="Crop", y="Yield",
            color="Yield", color_continuous_scale=["#d8f3dc","#1a472a"],
            title=f"Top crops by yield — {sel_state}",
        )
        fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                           margin=dict(t=40,b=10), height=300,
                           coloraxis_showscale=False, xaxis_tickangle=-40,
                           font=dict(family="DM Sans"))
        st.plotly_chart(fig2, use_container_width=True)

    # ── TAB 4: Season Trends ───────────────────────────────────────────────
    with tabs[3]:
        col1, col2 = st.columns(2)
        with col1:
            season_year = df.groupby(["Crop_Year","Season"])["Yield"].mean().reset_index()
            fig = px.line(
                season_year, x="Crop_Year", y="Yield", color="Season",
                color_discrete_sequence=PALETTE,
                title="Yield Trend by Season Over Years",
                markers=True,
            )
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                               margin=dict(t=40,b=10), height=340,
                               font=dict(family="DM Sans"))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            season_box = df[df["Yield"] <= df["Yield"].quantile(0.98)]
            fig2 = px.box(
                season_box, x="Season", y="Yield",
                color="Season", color_discrete_sequence=PALETTE,
                title="Yield Distribution by Season",
            )
            fig2.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                margin=dict(t=40,b=10), height=340,
                                showlegend=False,
                                font=dict(family="DM Sans"))
            st.plotly_chart(fig2, use_container_width=True)

        # Rainfall vs Yield scatter
        st.markdown("**Rainfall vs Yield**")
        sample = df[df["Yield"] <= df["Yield"].quantile(0.97)].sample(
            min(2000, len(df)), random_state=42
        )
        fig3 = px.scatter(
            sample, x="Annual_Rainfall", y="Yield", color="Season",
            color_discrete_sequence=PALETTE, opacity=0.6,
            title="Annual Rainfall vs Yield",
            trendline="ols",
        )
        fig3.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                            margin=dict(t=40,b=10), height=340,
                            font=dict(family="DM Sans"))
        st.plotly_chart(fig3, use_container_width=True)

    # ── TAB 5: Raw Data ────────────────────────────────────────────────────
    with tabs[4]:
        st.markdown("**Filter & browse the raw dataset**")
        fc1, fc2, fc3 = st.columns(3)
        with fc1: f_state  = st.selectbox("State",  ["All"] + sorted(df["State"].unique()))
        with fc2: f_crop   = st.selectbox("Crop",   ["All"] + sorted(df["Crop"].unique()))
        with fc3: f_season = st.selectbox("Season", ["All"] + sorted(df["Season"].unique()))

        fdf = df.copy()
        if f_state  != "All": fdf = fdf[fdf["State"]  == f_state]
        if f_crop   != "All": fdf = fdf[fdf["Crop"]   == f_crop]
        if f_season != "All": fdf = fdf[fdf["Season"] == f_season]

        st.caption(f"{len(fdf):,} records match filters")
        st.dataframe(fdf.reset_index(drop=True), use_container_width=True, height=420)

        csv = fdf.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Filtered CSV", csv,
                           "crop_yield_filtered.csv", "text/csv")