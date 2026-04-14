"""pages/price_forecast.py — Crop Price Trends & Forecast (MSP-based + trend simulation)"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pages.helpers import load_data

# ── MSP data (₹/quintal) from CACP — 2015 to 2024 ─────────────────────────
MSP_DATA = {
    "Rice": {
        2015:1410, 2016:1470, 2017:1550, 2018:1750, 2019:1815,
        2020:1868, 2021:1940, 2022:2015, 2023:2183, 2024:2300
    },
    "Wheat": {
        2015:1450, 2016:1525, 2017:1625, 2018:1735, 2019:1840,
        2020:1925, 2021:1975, 2022:2015, 2023:2125, 2024:2275
    },
    "Maize": {
        2015:1325, 2016:1365, 2017:1425, 2018:1700, 2019:1760,
        2020:1850, 2021:1870, 2022:1962, 2023:2090, 2024:2225
    },
    "Sugarcane": {
        2015:230,  2016:230,  2017:255,  2018:275,  2019:275,
        2020:285,  2021:290,  2022:305,  2023:315,  2024:340
    },
    "Groundnut": {
        2015:4030, 2016:4220, 2017:4450, 2018:4890, 2019:5090,
        2020:5275, 2021:5550, 2022:5850, 2023:6377, 2024:6783
    },
    "Soyabean": {
        2015:2600, 2016:2775, 2017:3050, 2018:3399, 2019:3710,
        2020:3880, 2021:3950, 2022:4300, 2023:4600, 2024:4892
    },
    "Cotton": {
        2015:3800, 2016:3860, 2017:4020, 2018:5150, 2019:5515,
        2020:5515, 2021:5726, 2022:6025, 2023:6620, 2024:7121
    },
    "Gram": {
        2015:3500, 2016:4000, 2017:4400, 2018:4620, 2019:4620,
        2020:4875, 2021:5100, 2022:5230, 2023:5440, 2024:5440
    },
    "Moong(Green Gram)": {
        2015:4850, 2016:4850, 2017:5225, 2018:6975, 2019:7050,
        2020:7196, 2021:7275, 2022:7755, 2023:8558, 2024:8682
    },
    "Arhar/Tur": {
        2015:4425, 2016:5050, 2017:5450, 2018:5675, 2019:5800,
        2020:5800, 2021:6000, 2022:6300, 2023:7000, 2024:7550
    },
    "Rapeseed &Mustard": {
        2015:3350, 2016:3350, 2017:3700, 2018:4000, 2019:4200,
        2020:4425, 2021:4650, 2022:5050, 2023:5450, 2024:5650
    },
    "Potato": {
        2015:487,  2016:492,  2017:503,  2018:512,  2019:519,
        2020:531,  2021:545,  2022:568,  2023:598,  2024:640
    },
}

CROP_UNITS = {
    "Sugarcane": "₹/quintal (FRP)", "Potato": "₹/quintal (approx)",
}
DEFAULT_UNIT = "₹/quintal (MSP)"


def forecast_prices(msp_dict, years_ahead=3):
    """Simple linear regression forecast."""
    years  = np.array(sorted(msp_dict.keys()))
    prices = np.array([msp_dict[y] for y in years])
    m, b   = np.polyfit(years, prices, 1)
    future = np.arange(years[-1] + 1, years[-1] + years_ahead + 1)
    return future, m * future + b, m


def render():
    st.markdown("""
    <div class="page-hero">
        <h1>📈 Price Forecast</h1>
        <p>MSP trends, year-on-year price growth, and 3-year price forecast for major crops</p>
    </div>
    """, unsafe_allow_html=True)

    df = load_data()

    # ── Selector ───────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        sel_crop = st.selectbox("Select Crop", sorted(MSP_DATA.keys()))
    with col2:
        compare  = st.multiselect("Compare with", 
                                  [c for c in MSP_DATA if c != sel_crop],
                                  default=["Wheat"] if sel_crop != "Wheat" else ["Rice"])
    with col3:
        forecast_yrs = st.slider("Forecast years ahead", 1, 5, 3)

    msp = MSP_DATA[sel_crop]
    unit = CROP_UNITS.get(sel_crop, DEFAULT_UNIT)

    # ── KPI metrics ────────────────────────────────────────────────────────
    latest_yr  = max(msp.keys())
    oldest_yr  = min(msp.keys())
    latest_msp = msp[latest_yr]
    prev_msp   = msp[latest_yr - 1]
    growth_yoy = ((latest_msp - prev_msp) / prev_msp) * 100
    growth_10y = ((latest_msp - msp[oldest_yr]) / msp[oldest_yr]) * 100
    cagr       = ((latest_msp / msp[oldest_yr]) ** (1/(latest_yr-oldest_yr)) - 1) * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"MSP {latest_yr}",  f"₹{latest_msp:,}",  f"+{growth_yoy:.1f}% YoY")
    c2.metric("10-Year Growth",    f"+{growth_10y:.1f}%")
    c3.metric("CAGR (10Y)",        f"{cagr:.1f}%")
    c4.metric("Unit",              unit)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── Price trend chart ──────────────────────────────────────────────────
    future_yrs, future_prices, slope = forecast_prices(msp, forecast_yrs)

    years  = sorted(msp.keys())
    prices = [msp[y] for y in years]

    fig = go.Figure()

    # Historical
    fig.add_trace(go.Scatter(
        x=years, y=prices,
        name=sel_crop,
        mode="lines+markers",
        line=dict(color="#2d6a4f", width=3),
        marker=dict(size=8, color="#1a472a"),
    ))

    # Forecast
    fig.add_trace(go.Scatter(
        x=list(future_yrs), y=list(future_prices),
        name="Forecast",
        mode="lines+markers",
        line=dict(color="#d4a017", width=2.5, dash="dash"),
        marker=dict(size=8, symbol="diamond", color="#d4a017"),
    ))

    # Forecast band
    fig.add_trace(go.Scatter(
        x=list(future_yrs) + list(future_yrs[::-1]),
        y=list(future_prices * 1.08) + list(future_prices[::-1] * 0.92),
        fill='toself', fillcolor='rgba(212,160,23,0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Confidence Band', showlegend=True,
    ))

    # Comparison crops
    comp_colors = ["#52b788", "#e74c3c", "#3b82f6", "#9b59b6"]
    for i, comp in enumerate(compare[:4]):
        comp_msp = MSP_DATA[comp]
        comp_yrs = sorted(comp_msp.keys())
        comp_prices = [comp_msp[y] for y in comp_yrs]
        fig.add_trace(go.Scatter(
            x=comp_yrs, y=comp_prices,
            name=comp,
            mode="lines+markers",
            line=dict(color=comp_colors[i], width=2, dash="dot"),
            marker=dict(size=6),
        ))

    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=30, b=10, l=0, r=0), height=380,
        xaxis=dict(showgrid=False, title="Year"),
        yaxis=dict(gridcolor="#f0f4f0", title=unit),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font=dict(family="DM Sans"),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Forecast table ─────────────────────────────────────────────────────
    st.markdown("<div class='section-title' style='font-size:1.1rem;'>🔮 Price Forecast</div>",
                unsafe_allow_html=True)

    fc_rows = []
    for yr, pr in zip(future_yrs, future_prices):
        prev = msp.get(yr - 1, prices[-1])
        fc_rows.append({
            "Year": int(yr),
            "Forecasted MSP (₹)": f"₹{int(pr):,}",
            "Expected Growth": f"+{((pr - prev)/prev*100):.1f}%",
            "Confidence": "High" if yr == future_yrs[0] else ("Medium" if yr == future_yrs[1] else "Low"),
        })
    fdf = pd.DataFrame(fc_rows)
    st.dataframe(fdf, use_container_width=True, hide_index=True)

    st.markdown("""
    <div style="color:#718096;font-size:.8rem;margin-top:.5rem;">
    ⚠️ Forecasts are based on linear trend extrapolation of historical MSP data.
    Actual prices may vary based on government policy, weather, and market conditions.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ── YoY growth bar ─────────────────────────────────────────────────────
    st.markdown("<div class='section-title' style='font-size:1.1rem;'>📊 Year-on-Year MSP Growth</div>",
                unsafe_allow_html=True)

    yoy_rows = []
    for i in range(1, len(years)):
        g = ((msp[years[i]] - msp[years[i-1]]) / msp[years[i-1]]) * 100
        yoy_rows.append({"Year": years[i], "Growth (%)": round(g, 2)})
    yoy_df = pd.DataFrame(yoy_rows)

    fig2 = px.bar(yoy_df, x="Year", y="Growth (%)",
                  color="Growth (%)",
                  color_continuous_scale=["#d8f3dc", "#2d6a4f"],
                  text=yoy_df["Growth (%)"].apply(lambda x: f"{x:.1f}%"))
    fig2.add_hline(y=yoy_df["Growth (%)"].mean(), line_dash="dash",
                   line_color="#d4a017",
                   annotation_text=f"Avg {yoy_df['Growth (%)'].mean():.1f}%",
                   annotation_position="top right")
    fig2.update_traces(textposition="outside")
    fig2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=30,b=10,l=0,r=0), height=300,
        coloraxis_showscale=False,
        font=dict(family="DM Sans"),
        xaxis=dict(showgrid=False),
        yaxis=dict(gridcolor="#f0f4f0"),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Cross-crop comparison ──────────────────────────────────────────────
    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='font-size:1.1rem;'>⚖️ 2024 MSP Comparison — All Crops</div>",
                unsafe_allow_html=True)

    all_2024 = {c: MSP_DATA[c][2024] for c in MSP_DATA if 2024 in MSP_DATA[c]}
    df_all   = pd.DataFrame(all_2024.items(), columns=["Crop", "MSP 2024 (₹/q)"]).sort_values(
        "MSP 2024 (₹/q)", ascending=False
    )

    fig3 = px.bar(df_all, x="Crop", y="MSP 2024 (₹/q)",
                  color="MSP 2024 (₹/q)",
                  color_continuous_scale=["#d8f3dc","#1a472a"],
                  text=df_all["MSP 2024 (₹/q)"].apply(lambda x: f"₹{x:,}"))
    fig3.update_traces(textposition="outside")
    fig3.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(t=30,b=10,l=0,r=0), height=340,
        coloraxis_showscale=False, xaxis_tickangle=-35,
        font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ── Full MSP table ─────────────────────────────────────────────────────
    with st.expander("📋 Full MSP History Table"):
        table_data = {crop: MSP_DATA[crop] for crop in MSP_DATA}
        msp_df = pd.DataFrame(table_data).T
        msp_df.index.name = "Crop"
        st.dataframe(
            msp_df.style.background_gradient(cmap="Greens", axis=1),
            use_container_width=True,
        )
        csv = msp_df.reset_index().to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download MSP Data", csv, "msp_data.csv", "text/csv")